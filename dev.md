
Fix: MOVE doesn't work instead a DELETE NEW is logged
----------------------------------------------------------

On win this doen't work

```python
def on_moved( self, event ):
  # ...
  if ... :
  else:   # doesn't work on win (maybe on linux, fix see dev.md)
    self._write_log_entry("MOVED", event.src_path, event.dest_path)
```

instead we get

```
Tu  0128 02:45  NEW       ...e\local\fil-sys-chg\debug\sample1.txt
Tu  0128 02:45  DELETE    ...l-sys-chg\debug\subfolder\sample1.txt
```

Solution: Merge 2 entries to MOVE


Fix: Prevent duplicate CHANGED events
----------------------------------------------------------

On win events appear as duplicate

AI: When you rename a file, it typically triggers 2 events

- A MOVED/RENAMED event (which we handle as RENAMED in our code)
- A MODIFIED event (which we handle as CHANGED in our code)

The MODIFIED event occurs because many file systems update certain metadata (like last modified time) when a file is renamed, even though the content hasn't changed. This is particularly common on Windows systems

Solution: currently track file sizes (alternative: hash)
