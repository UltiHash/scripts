#!/usr/bin/env python3
import boto3
import os
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: simple_upload.py <UltiHash URL> [file [file ...]]")
        print("\nSimple single-threaded script to outline file upload to UltiHash service")
        print("using boto3 library.")
        sys.exit(1)

    # connection to UltiHash S3 service
    uh_url = sys.argv[1]
    uh_service = boto3.client('s3', endpoint_url=uh_url)

    # all data will be stored under
    target_bucket_name = "bucket"
    try:
        uh_service.create_bucket(Bucket=target_bucket_name)
    except:
        pass

    total_uploaded = 0
    total_stored = 0

    # upload each file from command line and output real and effective size
    for id in range(2, len(sys.argv)):
        file = sys.argv[id]

        with open(file, 'rb') as f:
            response = uh_service.put_object(Bucket=target_bucket_name, Key=os.path.basename(file), Body=f)

            headers = response['ResponseMetadata']['HTTPHeaders']

            uploaded_bytes = int(headers['uh-original-size'])
            stored_bytes = int(headers['uh-effective-size'])

            total_uploaded += uploaded_bytes
            total_stored += stored_bytes

            print(f"uploaded {file} with {uploaded_bytes} real size and {stored_bytes} effective size")

    print(f"total uploaded bytes: {total_uploaded}, total stored bytes: {total_stored}")
    print(f"space savings: {100 * (total_uploaded - total_stored) / total_uploaded:.2f} %")
