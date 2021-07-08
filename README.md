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

For transcription, use Jaymon/transcribe on git, but run from dev branch, not master. Need to use downgraded versions of Jaymon/captain (v<4.0.0) and google-cloud-speech (trying with 2.0.0), and also needed a "lower version of FFMPG" (from old notes... no idea what it meant...).

Need FFMPEG to convert from mp4 to mp3:

```bash
ffmpeg -i <fi_name_original>.mp4 <fi_name_new>.mp3 11.05-live_Staff-Q-A-_640x360.mp3
```

Make sure running dev installation of jaymon/transcribe and using mp3, pipe output from stdin into file:

```bash
transcribe speech <path_to_file>.mp3 >> <path_to_file>.transcript
