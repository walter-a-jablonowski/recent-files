#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

class FileChangeHandler( FileSystemEventHandler ):

  def __init__( self, log_file, max_path_length=40 ):

    self.log_file        = log_file
    self.max_path_length = max_path_length
    self.file_sizes      = {}    # fix: prevent duplicate CHANGED events (see dev.md)
    self.last_delete     = None  # fix: MOVED doesn't work (see dev.md)
    
  def on_created( self, event ):

    if not event.is_directory:   # currently fil only

      try:

        # Fix: MOVED doesn't work (see dev.md)

        # when a NEW file has the same name and size as the last DELETED
        # from log replace the log entry with a MOVE

        new_size = os.path.getsize(event.src_path)  # also for fix: prevent duplicate CHANGED events (see dev.md)
        self.file_sizes[event.src_path] = new_size

        if self.last_delete:

          new_name = os.path.basename( event.src_path)
          old_name = os.path.basename( self.last_delete['path'])
          
          if( new_name == old_name and new_size == self.last_delete['size']):
            
            self._replace_last_entry("MOVED", self.last_delete['path'], event.src_path)
            self.last_delete = None
            return

        # regular NEW event
        self._write_log_entry("NEW", event.src_path)

      except OSError:  # for fix: prevent duplicate CHANGED events (see dev.md)
        pass           # file might be gone already

  def on_modified( self, event ):

    if not event.is_directory:

      try:
        new_size = os.path.getsize(event.src_path)
        old_size = self.file_sizes.get(event.src_path)
        
        # Fix: prevent duplicate CHANGED events (see dev.md) 
        # only log if size changed or we haven't seen this file before
        if old_size is None or new_size != old_size:
          self._write_log_entry("CHANGED", event.src_path)
          self.file_sizes[event.src_path] = new_size

      except OSError:
        pass  # file might be gone already

  def on_deleted( self, event ):

    if not event.is_directory:

      try:  # TASK: unsure
        file_size = os.path.getsize(event.src_path)
      except OSError:
        file_size = self.file_sizes.get(event.src_path)

      self.file_sizes.pop(event.src_path, None)  # remove from tracking
      
      self.last_delete = {  # fix: MOVED doesn't work (see dev.md)
        'path': event.src_path,
        'size': file_size
      }
      
      self._write_log_entry("DELETE", event.src_path)

  def on_moved( self, event ):

    if not event.is_directory:

      # Fix: prevent duplicate CHANGED events (see dev.md)
      try:
        self.file_sizes[event.dest_path] = os.path.getsize(event.dest_path)
      except OSError:
        pass
      self.file_sizes.pop(event.src_path, None)
      
      if os.path.dirname(event.src_path) == os.path.dirname(event.dest_path):
        self._write_log_entry("RENAMED", event.src_path, event.dest_path)  # same dir = rename
      else:  # doesn't work on win (maybe on linux, fix see dev.md)
        self._write_log_entry("MOVED", event.src_path, event.dest_path)    # different dir = move

  def _write_log_entry( self, event_type, src_path, dest_path = None ):

    """Write a log entry to the beginning of the file"""

    now = datetime.now()
    day = now.strftime("%a")[:2]  # get first 2 chars of weekday name
    date_time = now.strftime("%m%d %H:%M")
    
    src_path_formatted = self._format_path(src_path)
    if dest_path:
      dest_path_formatted = self._format_path(dest_path)
      entry = f"{day}  {date_time}  {event_type:<8}  {src_path_formatted}  -->  {dest_path_formatted}\n"
    else:
      entry = f"{day}  {date_time}  {event_type:<8}  {src_path_formatted}\n"
      
    try:
      with open(self.log_file, 'r') as f:
        content = f.read()
    except FileNotFoundError:
      content = ""
      
    with open(self.log_file, 'w') as f:
      f.write(entry + content)

  def _replace_last_entry( self, event_type, src_path, dest_path ):

    """Replace the last log entry with a new one"""

    try:
      with open(self.log_file, 'r') as f:
        lines = f.readlines()
      
      if len(lines) > 1:
        content = ''.join(lines[1:])  # Keep all but first line
      else:
        content = ""

      now = datetime.now()
      day = now.strftime("%a")[:2]
      date_time = now.strftime("%m%d %H:%M")
      
      src_path_formatted  = self._format_path(src_path)
      dest_path_formatted = self._format_path(dest_path)
      entry = f"{day}  {date_time}  {event_type:<8}  {src_path_formatted}  -->  {dest_path_formatted}\n"
      
      with open(self.log_file, 'w') as f:
        f.write(entry + content)
    except (IOError, IndexError):
      # If we can't read/write the log file, fall back to normal write
      self._write_log_entry(event_type, src_path, dest_path)

  def _format_path( self, path ):

    """Format path to have a maximum length, adding ... at the start if needed"""
    
    path_str = str(path)
    if len(path_str) <= self.max_path_length:
      return path_str
    return f"...{path_str[-(self.max_path_length-3):]}"

def monitor_directory( path, log_file ):

  """Start monitoring a dir for changes"""

  abs_path = os.path.abspath(path)
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
    print("\nMonitoring stopped")
  observer.join()

if __name__ == "__main__":

  if len(sys.argv) != 3:
    print("Usage: python file_sys_chg.py <dir> <log_file>")
    sys.exit(1)
    
  monitor_directory(sys.argv[1], sys.argv[2])
