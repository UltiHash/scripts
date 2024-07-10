#!/usr/bin/env python3

import argparse
import concurrent.futures
import boto3
import botocore
import pathlib
import sys
import time
import tqdm

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
    parser.add_argument('--read-timeout', help='read timeout in seconds',
        action='store', default=60, type=int)
    parser.add_argument('--max-attempts', help='maximum number of download attempts',
        action='store', default=3, type=int)

    return parser.parse_args()


class downloader:
    def __init__(self, config):
        self.threads = concurrent.futures.ThreadPoolExecutor(max_workers=config.jobs)

        s3_cnf = botocore.config.Config(
            read_timeout=config.read_timeout,
            retries = {
                'max_attempts': config.max_attempts,
                'mode': 'standard'
            })

        self.s3 = boto3.client('s3', endpoint_url=config.url[0], config=s3_cnf)
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
        response = self.s3.get_object(Bucket=bucket, Key=key)
        with open(local_path, "wb+") as f:
            body = response["Body"].read()
            cb(len(body))
            f.write(body)

    def list_objects(self, bucket):
        paginator = self.s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket):
            for entry in page['Contents']:
                yield entry

    def push(self, bucket, key):
        local_path = self.config.path / bucket / key
        return self.threads.submit(self.download, bucket, key, local_path)

    def set_total(self, total):
        self.progress = tqdm.tqdm(unit='B', unit_scale=True, total=total)
        self.progress.update(self.count_buffer)
        self.count_buffer = 0

def download(config):
    
    dn = downloader(config)
    results = []
    size_total = 0

    start = time.monotonic()

    for bucket in config.bucket:
        for entry in dn.list_objects(bucket):
            results += [ (entry['Key'],  dn.push(bucket, entry['Key'])) ]
            size_total += entry['Size']

    dn.set_total(size_total)

    for job in results:
        try:
            job[1].result()
        except Exception as e:
            print(f"Error downloading {job[0]}: {str(e)}", file=sys.stderr)

    end = time.monotonic()
    seconds = end - start
    mb = size_total / (1024 * 1024)

    print(f"average download speed: {mb/seconds} MB/s")
    return float(mb)/seconds

if __name__ == "__main__":
    config = parse_args()
    download(config)
