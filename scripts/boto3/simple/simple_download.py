#!/usr/bin/env python3
import boto3
import os
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: simple_upload.py <endpoint> [file [file ...]]")
        sys.exit(1)

    # connection to S3 service
    url = sys.argv[1]
    s3 = boto3.client('s3', endpoint_url=url,
        aws_access_key_id='', aws_secret_access_key='')

    # all data will be queried from this bucket
    bucket_name = "bucket"
    s3.create_bucket(Bucket=bucket_name)

    # download each file from command line and store it in the current working directory
    for id in range(2, len(sys.argv)):
        file = sys.argv[id]

        response = s3.get_object(Bucket=bucket_name, Key=os.path.basename(file))
        with open(file, 'wb') as f:
            f.write(response['Body'].read())

            print(f"downloaded {file}")
