#!/usr/bin/env python3

import argparse
import concurrent.futures
import pprint
import boto3
import os
import pathlib
import sys
import tqdm

AWS_KEY_ID="key-id"
AWS_KEY_SECRET="secret"

def parse_args():
    parser = argparse.ArgumentParser(
        prog='UH download',
        description='Downloading files from UH cluster')

    parser.add_argument('-C', '--path', help='target directory, will be created if not existing',
        type=pathlib.Path, default='.')
    parser.add_argument('-u', '--url', help='override default S3 endpoint',
        nargs=1, default='http://localhost:8080', dest='url')
    parser.add_argument('-v', '--verbose', help='write additional information to stdout',
        action='store_true', dest='verbose')
    parser.add_argument('bucket', help='download all files of the given bucket',
        action='store', nargs='+')
    parser.add_argument('-j', '--jobs', help='number of concurrent jobs',
        action='store', default=8, type=int)

    return parser.parse_args()


class downloader:
    def __init__(self, s3, config):
        self.threads = concurrent.futures.ThreadPoolExecutor(max_workers=config.jobs)
        self.s3 = boto3.client('s3', endpoint_url=config.url[0],
            aws_access_key_id=AWS_KEY_ID, aws_secret_access_key=AWS_KEY_SECRET)
        self.config = config
        self.progress = None
        self.count_buffer = 0

    def download(self, bucket, key, local_path):
        def cb(count):
            if self.progress is not None:
                self.progress.update(count)
            else:
                self.count_buffer += count

        local_path.parent.mkdir(parents=True, exist_ok=True)
        self.s3.download_file(Bucket=bucket, Key=key, Filename=local_path, Callback=cb)

    def list_objects(self, bucket):
        return self.s3.list_objects_v2(Bucket=bucket, MaxKeys=10000)

    def push(self, bucket, key):
        local_path = self.config.path / bucket / key
        return (self.threads.submit(self.download, bucket, key, local_path), bucket, key, local_path)

    def set_total(self, total):
        self.progress = tqdm.tqdm(unit='b', unit_scale=True, total=total)
        self.progress.update(self.count_buffer)
        self.count_buffer = 0

if __name__ == "__main__":
    config = parse_args()

    dn = downloader(s3, config)
    results = []
    size_total = 0

    for bucket in config.bucket:
        resp = dn.list_objects(bucket)
        for entry in resp['Contents']:
            results += [ (entry['Key'],  dn.push(bucket, entry['Key'])) ]
            size_total += entry['Size']

    dn.set_total(size_total)

    for job in results:
        try:
            job[1].result()
        except Exception as e:
            print(f"Error uploading {job[0]}: {str(e)}", file=sys.stderr)

    print()
