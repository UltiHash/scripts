# Overview

Concurrent UltiHash upload script. Upload data recursively to UltiHash cluster using boto3 library to access the S3 API.

# Requirements

- Python 3
- boto3 library installed

# Installation
Create a virtual environment to hold the Python libraries:

```
$> python3 -m venv venv
$> . venv/bin/activate
```

Install all requirements:

```
$> pip install --requirement requirements.txt
```
Before executing the script make sure the AWS credentials are properly set:
- as [environment variables](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html#envvars-set)
- as [instance profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html#cli-configure-files-methods)

# Usage
To upload a folder to an UH cluster running locally:

```
$> ./uh_upload.py $PATH_TO_FOLDER
```

Upload a folder to a given S3 instance

```
$> ./uh_upload.py --url http://uh.my-domain.net $PATH_TO_FOLDER
```

Override the default target bucket:

```
$> ./uh_upload.py --bucket MY_BUCKET $PATH_TO_FOLDER
```
