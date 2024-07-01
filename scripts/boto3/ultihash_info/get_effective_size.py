#!/usr/bin/env python3
import argparse
import boto3
import botocore
import json

AWS_KEY_ID="key-id"
AWS_KEY_SECRET="secret"

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

    s3 = boto3.client('s3', endpoint_url=config.url, config=s3_cnf,
            aws_access_key_id=AWS_KEY_ID, aws_secret_access_key=AWS_KEY_SECRET)
    response = s3.get_object(Bucket="ultihash", Key="v1/metrics/cluster")
    body = response['Body']#.read()
    jbody = json.load(body)
    effective_size = jbody['effective_data_size']
    print(f"Ultihash effective size is {effective_size} MB")
    return effective_size

if __name__ == "__main__":
    config = parse_args()
    
    get_effective_size(config)
    
