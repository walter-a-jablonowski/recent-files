#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

class FileChangeHandler(FileSystemEventHandler):

  def __init__( self, log_file, max_path_length=40 ):

    self.log_file        = log_file
    self.max_path_length = max_path_length
    self.file_sizes      = {}     # prevent duplicate CHANGED events
    
  def _write_log_entry( self, event_type, src_path, dest_path = None ):

    """Write a log entry to the beginning of the file"""

    now = datetime.now()
    day = now.strftime("%a")[:2]  # get first 2 chars of weekday name
    date_time = now.strftime("%m%d %H:%M")
    
    # Format log entry

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

  def on_created( self, event ):

    if not event.is_directory:

      # Track file sizes to prevent duplicate CHANGED events
      try:
        self.file_sizes[event.src_path] = os.path.getsize(event.src_path)
      except OSError:
        pass  # File might be gone already

      self._write_log_entry("NEW", event.src_path)

  def on_modified( self, event ):

    if not event.is_directory:

      # Track file sizes to prevent duplicate CHANGED events
      try:
        new_size = os.path.getsize(event.src_path)
        old_size = self.file_sizes.get(event.src_path)
        
        # Only log if size changed or we haven't seen this file before
        if old_size is None or new_size != old_size:
          self._write_log_entry("CHANGED", event.src_path)
          self.file_sizes[event.src_path] = new_size
      except OSError:
        pass  # File might be gone already

  def on_deleted( self, event ):

    if not event.is_directory:
      self.file_sizes.pop(event.src_path, None)  # Remove from tracking
      self._write_log_entry("DELETE", event.src_path)

  def on_moved( self, event ):

    if not event.is_directory:
      # Track file sizes to prevent duplicate CHANGED events
      # Update size tracking for the new path
      try:
        self.file_sizes[event.dest_path] = os.path.getsize(event.dest_path)
      except OSError:
        pass
      # Remove old path from tracking
      self.file_sizes.pop(event.src_path, None)
      
      if os.path.dirname(event.src_path) == os.path.dirname(event.dest_path):
        # Same directory = rename
        self._write_log_entry("RENAMED", event.src_path, event.dest_path)
      else:
        # Different directory = move
        self._write_log_entry("MOVED", event.src_path, event.dest_path)

  def _format_path( self, path ):

    """Format path to have a maximum length, adding ... at the start if needed"""
    
    path_str = str(path)
    if len(path_str) <= self.max_path_length:
      return path_str
    return f"...{path_str[-(self.max_path_length-3):]}"

def monitor_directory( path, log_file ):

  """Start monitoring a dir for changes"""

  # Create absolute paths
  abs_path = os.path.abspath(path)
  abs_log_file = os.path.abspath(log_file)
  
  # Ensure the base directory exists
  if not os.path.exists(abs_path):
    print(f"Error: Directory '{abs_path}' does not exist")
    sys.exit(1)
    
  # Create event handler and observer
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
