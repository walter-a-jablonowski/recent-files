
- [-] Rename has only the new file name
- Duplicate entries in log file for some reason

  - [x] maybe compare file size doesn't change, change it in file, json or .sys
    - In-Memory Dictionary `self.file_sizes = {}  # path -> size`

- [x] MOVE doesn't work instead a DELETE NEW is logged

    - solved the simple way (undone)
    - maybe event simpler: just merge log entries if DELETE NEW with same file name appear in log

- [x] Shorten log file if too long


Advanced
---------------------------------------------------------

- [ ] looks like duplicate DELETE when using with gd
- [ ] less information: a liitle abstract to reduce the overhead

  - only watch fils an flds twith certain string in name (1 -)

- [ ] see TASKS

- [ ] can we ask AI to somehow clean up the implementation a bit witout destrying functionality?
- [ ] maybe Python Code to a Standalone APK

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
