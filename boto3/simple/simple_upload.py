#!/usr/bin/env python3
# Copyright 2026 UltiHash Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
