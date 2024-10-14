# Overview

Concurrent UltiHash script for getting the global effective size. 

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

# Usage
To get the effective size of the data stored in UH cluster running locally:

```
$> ./uh_upload.py 
```

Upload a folder to a given UltiHash instance

```
$> ./uh_upload.py --url http://uh.my-domain.net
```
