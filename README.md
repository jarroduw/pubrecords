pubrecords

This is a repository for parsing a public records request.

It consists of a set of ingest scripts that will read through expected formats. Directory structure at pipeline is expected to be:

```
root
root/target_dir_name/
root/done/target_dir_name/
root/issues/target_dir_name/
```

Files when parsed are moved from `target_dir_name` into either `done/target_dir_name` or `issues/target_dir_name` (when an issue is encountered).

To parse everything, run `parseFolder.sh` with a single command line argument with the `target_dir_name` (include trailing slash).
