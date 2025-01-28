
- [-] Rename has only the new file name
- Duplicate entries in log file for some reason

  - [x] maybe compare file size doesn't change, change it in file, json or .sys
    - In-Memory Dictionary `self.file_sizes = {}  # path -> size`

- [ ] MOVE doesn't work instead a DELETE NEW is logged

    - solved the simple way (undone)
    - maybe event simpler: just merge log entries if DELETE NEW with same file name appear in log

- [ ] Shorten log file if too long


Advanced
---------------------------------------------------------

- [ ] maybe Python Code to a Standalone APK

### Problem with duplicate log entries

AI: When you rename a file, it typically triggers 2 events

- A MOVED/RENAMED event (which we handle as RENAMED in our code)
- A MODIFIED event (which we handle as CHANGED in our code)

The MODIFIED event occurs because many file systems update certain metadata (like last modified time) when a file is renamed, even though the content hasn't changed. This is particularly common on Windows systems

- [ ] Instead of comparing file sizes to filter out duplicate log entries we could use hash (more precise)
- [ ] also remember betweenn runs (maybe unneeded unless we have similar problems)

  - json in app folder (sqlite cause of performance ?)
  - .sys/fil_chgs/duplicates_cache.json
  - less good (unreadable)
    ```
    Su  0126 11:04  NEW      .../file.txt  [size:1234]  source: c:/full/.../...
    ```

### C++ variant if needed for performance

```c
HANDLE hDir = CreateFile(
  "C:\\Path\\To\\Directory",
  FILE_LIST_DIRECTORY,
  FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
  NULL,
  OPEN_EXISTING,
  FILE_FLAG_BACKUP_SEMANTICS,
  NULL
);

char buffer[1024];
DWORD bytesReturned;
while (ReadDirectoryChangesW(
  hDir, buffer, sizeof(buffer), TRUE,
  FILE_NOTIFY_CHANGE_FILE_NAME | FILE_NOTIFY_CHANGE_DIR_NAME | FILE_NOTIFY_CHANGE_SIZE,
  &bytesReturned, NULL, NULL)) 
{
  // Process changes
}
CloseHandle(hDir);
```
