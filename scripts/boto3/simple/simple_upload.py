#!/usr/bin/env python3
import boto3
import os
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: simple_upload.py <endpoint> [file [file ...]]")
        print("\nSimple single-threaded script to outline file upload to S3 service")
        print("using boto3 library.")
        sys.exit(1)

    # connection to S3 service
    url = sys.argv[1]
    target_s3 = boto3.client('s3', endpoint_url=url,
        aws_access_key_id='', aws_secret_access_key='')

    # all data will be stored under
    target_bucket_name = "bucket"
    target_s3.create_bucket(Bucket=target_bucket_name)

    # upload each file from command line and output real and effective size
    for id in range(2, len(sys.argv)):
        file = sys.argv[id]

        with open(file, 'rb') as f:
            response = target_s3.put_object(Bucket=target_bucket_name, Key=os.path.basename(file), Body=f)

            headers = response['ResponseMetadata']['HTTPHeaders']

            uploaded_bytes = float(headers['uh-original-size'])
            stored_bytes = float(headers['uh-effective-size'])

            print(f"uploaded {file} with {uploaded_bytes} real size and {stored_bytes} effective size")
