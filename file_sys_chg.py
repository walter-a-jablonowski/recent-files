#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import configparser

class FileChangeHandler( FileSystemEventHandler ):

  def __init__( self, log_file, max_path_length=40 ):

    self.log_file = log_file
    self.max_path_length = max_path_length
    self.log_entries = []  # List of dicts containing last 10 see write_log_entry {time, event_type, path, target_path, size}
    
    self.config = configparser.ConfigParser()

    try:
      self.config.read('config.ini')
      self.max_log_lines = int(self.config['Archive']['max_log_lines'])
      self.archive_folder = self.config['Archive']['archive_folder']
      self.ignored_files = [f.strip() for f in self.config.get('Ignore', 'files', fallback='').split(',')]
    except:
      self.max_log_lines = 100   # default
      self.archive_folder = 'archive'
      self.ignored_files = []

  def _should_ignore( self, path ):

    """Check if the file should be ignored based on config"""

    filename = os.path.basename(path)
    return filename in self.ignored_files

  def on_created( self, event ):

    if not self._should_ignore(event.src_path):
      try:
        file_size = os.path.getsize(event.src_path) if not event.is_directory else None
        
        # Check if last entry was DELETE and merge into MOVED if paths match
        if self.log_entries and self.log_entries[-1]['event_type'] == 'DELETE':
          last_entry = self.log_entries[-1]
          new_name = os.path.basename(event.src_path)
          old_name = os.path.basename(last_entry['path'])
          
          if new_name == old_name:
            self._replace_last_entry("MOVED", last_entry['path'], event.src_path)
            return

        # Check for duplicate event
        if self.log_entries and self._is_duplicate_event("NEW", event.src_path):
          return
            
        # Regular NEW event
        self._write_log_entry("NEW", event.src_path, size=file_size)

      except OSError:
        pass  # File might be gone already

  def on_modified( self, event ):

    if not self._should_ignore(event.src_path):
      if not event.is_directory:  # Only track CHANGED for files, not directories
        try:
          # Skip if this is a CHANGED event right after a RENAME/MOVE for the same file
          if self.log_entries and len(self.log_entries) > 0:
            last_entry = self.log_entries[-1]
            if( last_entry['event_type'] in ['RENAMED', 'MOVED'] and 
                last_entry['target_path'] and 
                os.path.abspath(event.src_path) == os.path.abspath(last_entry['target_path'])):
              return

          new_size = os.path.getsize(event.src_path)
          
          # Check for duplicate event
          if self.log_entries and self._is_duplicate_event("CHANGED", event.src_path):
            return
            
          # Check if size changed from last known size
          last_size = None
          for entry in reversed(self.log_entries):
            if entry['path'] == event.src_path and entry['size'] is not None:
              last_size = entry['size']
              break
              
          if last_size is None or new_size != last_size:
            self._write_log_entry("CHANGED", event.src_path, size=new_size)

        except OSError:
          pass  # File might be gone already

  def on_deleted( self, event ):

    if not self._should_ignore(event.src_path):
      try:
        file_size = os.path.getsize(event.src_path) if not event.is_directory else None
      except OSError:
        # Try to get last known size from log entries
        file_size = None
        for entry in reversed(self.log_entries):
          if entry['path'] == event.src_path and entry['size'] is not None:
            file_size = entry['size']
            break
      
      # Check for duplicate event
      if self.log_entries and self._is_duplicate_event("DELETE", event.src_path):
        return
        
      self._write_log_entry("DELETE", event.src_path, size=file_size)

  def on_moved( self, event ):

    if not (self._should_ignore(event.src_path) or self._should_ignore(event.dest_path)):
      try:
        file_size = os.path.getsize(event.dest_path) if not event.is_directory else None
      except OSError:
        file_size = None
        
      # Check for duplicate event
      if self.log_entries and self._is_duplicate_event("MOVED", event.src_path, event.dest_path):
        return
        
      if os.path.dirname(event.src_path) == os.path.dirname(event.dest_path):
        self._write_log_entry("RENAMED", event.src_path, dest_path=event.dest_path, size=file_size)
      else:
        self._write_log_entry("MOVED", event.src_path, dest_path=event.dest_path, size=file_size)


  # Helper

  def _is_duplicate_event( self, event_type, path, target_path=None ):

    """Check if this event is a duplicate of the last entry"""

    if not self.log_entries:
      return False
      
    last_entry = self.log_entries[-1]
    return (last_entry['event_type'] == event_type and 
            last_entry['path'] == path and 
            last_entry['target_path'] == target_path)

  def _write_log_entry( self, event_type, src_path, dest_path=None, size=None ):

    """Write a log entry to the beginning of the file and update in-memory log"""

    now = datetime.now()
    day = now.strftime("%a")[:2]  # Get first 2 chars of weekday name
    date_time = now.strftime("%m%d %H:%M")
    
    src_path_formatted = self._format_path(src_path)
    
    if dest_path:
      dest_path_formatted = os.path.basename(dest_path) if event_type == "RENAMED" else self._format_path(dest_path)
      entry = f"{day}  {date_time}  {event_type:<8}  {src_path_formatted}  -->  {dest_path_formatted}\n"
    else:
      entry = f"{day}  {date_time}  {event_type:<8}  {src_path_formatted}\n"
      
    try:
      with open(self.log_file, 'r') as f:
        content = f.readlines()
    except FileNotFoundError:
      content = []
      
    # Check if we need to archive
    if len(content) >= self.max_log_lines:
      self._archive_log_entries(content)
      content = content[:len(content)//2]  # Keep first (newer) half of the lines
      
    with open(self.log_file, 'w') as f:
      f.write(entry + ''.join(content))
      
    # Update in-memory log entries
    self.log_entries.append({
      'time': now,
      'event_type': event_type,
      'path': src_path,
      'target_path': dest_path,
      'size': size
    })
    
    # Keep only last 10 entries
    if len(self.log_entries) > 10:
      self.log_entries.pop(0)

  def _replace_last_entry( self, event_type, src_path, dest_path ):

    """Replace the last log entry with a new one"""

    try:
      with open(self.log_file, 'r') as f:
        lines = f.readlines()
      
      if len(lines) > 1:
        content = ''.join(lines[1:])  # keep all but first line
      else:
        content = ""

      now = datetime.now()
      day = now.strftime("%a")[:2]
      date_time = now.strftime("%m%d %H:%M")
      
      src_path_formatted  = self._format_path(src_path)
      dest_path_formatted = os.path.basename(dest_path) if event_type == "RENAMED" else self._format_path(dest_path)
      entry = f"{day}  {date_time}  {event_type:<8}  {src_path_formatted}  -->  {dest_path_formatted}\n"
      
      with open(self.log_file, 'w') as f:
        f.write(entry + content)
        
      # Update the last in-memory entry
      if self.log_entries:
        last_entry = self.log_entries[-1]
        self.log_entries[-1] = {
          'time': now,
          'event_type': event_type,
          'path': src_path,
          'target_path': dest_path,
          'size': last_entry['size']  # preserve the size from DELETE event
        }
    
    except (IOError, IndexError):
      # If we can't read/write the log file, fall back to normal write
      self._write_log_entry(event_type, src_path, dest_path)

  def _format_path( self, path ):

    """Format path to have a maximum length, adding ... at the start if needed"""
    
    path_str = str(path)

    if len(path_str) <= self.max_path_length:
      return path_str
    return f"...{path_str[-(self.max_path_length-3):]}"

  def _archive_log_entries( self, content ):

    """Archive the older half of log entries to a timestamped file"""
    
    watch_dir    = os.path.dirname( os.path.abspath(self.log_file))
    archive_path = os.path.join( watch_dir, self.archive_folder)
    os.makedirs(archive_path, exist_ok=True)
    
    timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_file = os.path.join(archive_path, f"{timestamp}.txt")
    
    with open(archive_file, 'w') as f:
      f.write(''.join(content[len(content)//2:]))  # archive second (older) half


# App

def observe_directory( path, log_file ):

  """Start observing a dir for changes"""

  abs_path     = os.path.abspath(path)
  abs_log_file = os.path.abspath(log_file)
  
  if not os.path.exists(abs_path):  # ensure the base directory exists
    print(f"Error: Directory '{abs_path}' does not exist")
    sys.exit(1)
    
  event_handler = FileChangeHandler(abs_log_file)
  observer = Observer()
  observer.schedule(event_handler, abs_path, recursive=True)
  
  print(f"Starting file sys changes for: {abs_path}")
  print(f"Log file: {abs_log_file}")
  print("Press Ctrl+C to exit")
  
  observer.start()

  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()
    print("\nobserving stopped")
  observer.join()


if __name__ == "__main__":

  if len(sys.argv) != 3:
    print("Usage: python file_sys_chg.py <dir> <log_file>")
    sys.exit(1)
    
  observe_directory(sys.argv[1], sys.argv[2])
