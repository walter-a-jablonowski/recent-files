
## Fix: Track file sizes to prevent duplicate CHANGED events

AI: When you rename a file, it typically triggers 2 events

- A MOVED/RENAMED event (which we handle as RENAMED in our code)
- A MODIFIED event (which we handle as CHANGED in our code)

The MODIFIED event occurs because many file systems update certain metadata (like last modified time) when a file is renamed, even though the content hasn't changed. This is particularly common on Windows systems
