<a id="top"></a>
<div>
<h1 align="center">HowTo UltiHash</h1>
  <p align="center">
Collection of most common integrations code samples to work with UltiHash storage solution.
  </p>
</div>

## Getting Started

Simply download suitable sample script for your use-case and run it close to the source of data you wish to upload. 

Currently list of available sample scripts is rather short, but we are working on extending it. Star to follow on our updates.

For additional informaition, please refer to our documentation: https://docs.ultihash.io/

Upload a folder:

```bash
./boto3/multithread_upload/uh_upload.py --url http://localhost:8080 -B xxx -e <source_folder>
```

Download the bucket:

```bash
./boto3/multithread_download/uh_download.py xxx --url http://localhost:8080 -C <target_folder> --delete-path
```

You'd better use ramdisk folder as a target folder for download, as it will be much faster and perform stabler.

Adding --delete-path option will remove the target folder before download, so you're download doesn't do any hidden remove operation which may slow down the process.
