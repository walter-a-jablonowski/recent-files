
Can you make a python app that logs file system changes in a define base folder and all of its sub folders?

Output goes in a text file, the most recent entry is the first

```
Su  0126 11:04  NEW      .../my/sub/fld/file.txt
Su  0126 11:03  CHANGED  .../my/sub/fld/file.txt
Su  0126 11:02  RENAMED  .../my/sub/fld/file.txt  -->  .../my/sub/fld/file1.txt
Su  0126 11:01  MOVED    .../my/sub/fld/file.txt  -->  .../my/sub2/fld/file.txt
Su  0126 11:00  DELETE   .../my/sub/fld/file.txt
```

Format is similar tsv, each field seperated with 2 spaces (be sure to align the cols vertically)

Fields

- Day of week: Mo-Su
- Date time:   MMDD HH:MM (skip the year)
- Type of change
- File path: cause we have long paths we only save a certain amount of chars, and abbreviate with "..." in front
- some entries use am arrow and a second gile path as seen in the samples above
