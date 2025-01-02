# PyTorch Integration

This document provides information regarding the integration between UltiHash and PyTorch.
Install the S3 connector for PyTorch:
```bash
pip install s3torchconnector
```
Below is an example of the PyTorch configuration that connects it with the UltiHash cluster.
```python
import s3torchconnector

# Define S3 region (could be any, since the custom S3 endpoint is used)
REGION = "us-east-1"
# Define the endpoint URL for the UltiHash cluster
ENDPOINT_URL = "https://ultihash.cluster"

# Enforce the path style URLs
config = s3torchconnector.S3ClientConfig(force_path_style=True)

# EXAMPLE 1: Create a dataset from the data stored on the UltiHash bucket named "test-data"
dataset = s3torchconnector.S3MapDataset.from_prefix(
    "s3://test-data/", 
    endpoint=ENDPOINT_URL, 
    region=REGION, 
    s3client_config=config
)

# EXAMPLE 2: Create a checkpoint
checkpoint = s3torchconnector.S3Checkpoint(
    region=REGION, 
    endpoint=S3_ENDPOINT, 
    s3client_config=config
)
```
