# File sys changes

[ DEPRECATED ] This was replaced by recent-files-2

-----------

```
Su  0126 11:04  NEW      .../my/sub/fld/file.txt
Su  0126 11:03  CHANGED  .../my/sub/fld/file.txt
Su  0126 11:02  RENAMED  .../my/sub/fld/file.txt  -->  file1.txt
Su  0126 11:01  MOVED    .../my/sub/fld/file.txt  -->  .../my/sub2/fld/file.txt
Su  0126 11:00  DELETE   .../my/sub/fld/file.txt
```

## Version

- **0.1.0** Observes all files
  - currently only file no dir changes
  - some duplicates may appear in log
- **Current**
  - also observe dir changes
  - simplified members, merge all kind of duplicates

## Usage

Requirements

- Python 3.x
- watchdog 3.0.0

```bash
pip install -r requirements.txt
python file_sys_chg.py <base_dir> <log_file>
python file_sys_chg.py "debug" "file_changes.log" 
```

see [start.bat](start.bat), move in win startup

## Dev

see [dev](dev.md)

## License

Copyright (C) Walter A. Jablonowski 2025, free under [MIT license](LICENSE)

This app is build upon Python and free software

[Privacy](https://walter-a-jablonowski.github.io/privacy.html) | [Legal](https://walter-a-jablonowski.github.io/imprint.html)
