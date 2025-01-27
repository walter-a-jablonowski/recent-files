
- [-] Rename has only the new file name
- [ ] Duplicate entries in log file for some reason (or filter)
  - maybe file size doesn't change, chage it in file or json
- [ ] MOVE doesn't work instead a DELETE NEW CHANGED is logged
- [ ] Shorten log file if too long


Advanced
---------------------------------------------------------

- Converting Python Code to a Standalone APK
- C++ variant if needed for performance

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
