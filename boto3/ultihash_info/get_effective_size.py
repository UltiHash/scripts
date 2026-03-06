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

import argparse
import boto3
import botocore
import json

def parse_args():
    parser = argparse.ArgumentParser(
        prog='UH Stats',
        description='Statistics from UH cluster')

    parser.add_argument('-u', '--url', help='override default S3 endpoint',
        default='http://localhost:8080', dest='url')

    return parser.parse_args()

def get_effective_size(config):
    s3_cnf = botocore.config.Config(
        read_timeout=10,
        retries = {
            'max_attempts': 3,
            'mode': 'standard'
        })

    s3 = boto3.client('s3', endpoint_url=config.url, config=s3_cnf)
    response = s3.get_object(Bucket="ultihash", Key="v1/metrics/cluster")
    body = response['Body']
    jbody = json.load(body)
    effective_size = jbody['effective_data_size']
    print(f"Ultihash effective size is {effective_size} MB")
    return effective_size

if __name__ == "__main__":
    config = parse_args()
    
    get_effective_size(config)
    
