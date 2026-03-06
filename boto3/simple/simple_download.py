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
        print("usage: simple_download.py <UltiHash URL> [file [file ...]]")
        print("\nSimple single-threaded script to outline download from UltiHash service")
        print("using boto3 library.")
        sys.exit(1)

    # connection to UltiHash S3 service
    uh_url = sys.argv[1]
    uh_service = boto3.client('s3', endpoint_url=uh_url)

    # all data will be queried from this bucket
    source_bucket_name = "bucket"

    # download each file from command line and store it in the current working directory
    for id in range(2, len(sys.argv)):
        file = sys.argv[id]

        response = uh_service.get_object(Bucket=source_bucket_name, Key=os.path.basename(file))
        with open(file, 'wb') as f:
            f.write(response['Body'].read())

            print(f"downloaded {file}")
