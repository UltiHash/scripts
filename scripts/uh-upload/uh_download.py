#!/usr/bin/env python3

import argparse
import concurrent.futures
import pprint
import boto3
import os
import pathlib
import sys
import time

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
    def __init__(self, s3, config, prg):
        self.s3 = s3
        self.threads = concurrent.futures.ThreadPoolExecutor(max_workers=config.jobs)
        self.config = config
        self.prg = prg

    def download(self, bucket, key, local_path):
        local_path.parent.mkdir(parents=True, exist_ok=True)

        with open(local_path, 'wb') as f:
            resp = self.s3.get_object(Bucket=bucket, Key=key)
            body = resp['Body'].read()
            f.write(body)

            return len(body)

    def push(self, bucket, key):
        local_path = self.config.path / bucket / key
        return (self.threads.submit(self.download, bucket, key, local_path), bucket, key, local_path)

class progress_bar(object):
    def __init__(self, start):
        self.files = 0
        self.done = 0
        self.downloaded = 0
        self.start = start

    def update(self, downloaded):
        self.done += 1
        self.downloaded += downloaded

    def print(self):
        elapsed_s = (time.monotonic_ns() - self.start) / 1000000000
        downloaded_mb = self.downloaded / (1024 * 1024)

        print(f"\rDownloaded {downloaded_mb: .02f} MB of data @ {downloaded_mb / elapsed_s: .02f} MB/s, " +
              f"{ 100 * self.done / self.files: .02f} % ",
              end='')

if __name__ == "__main__":
    config = parse_args()

    s3 = boto3.client('s3', endpoint_url=config.url[0],
        aws_access_key_id=AWS_KEY_ID, aws_secret_access_key=AWS_KEY_SECRET)

    start_time = time.monotonic_ns()
    prg = progress_bar(start_time)

    dn = downloader(s3, config, prg)

    results = []

    for bucket in config.bucket:
        resp = s3.list_objects_v2(Bucket=bucket,MaxKeys=10000)
        for entry in resp['Contents']:
            results += [ dn.push(bucket, entry['Key']) ]

    prg.files = len(results)

    while len(results) > 0:
        results_remain = []

        for f in results:
            if f[0].done():
                try:
                    info = f[0].result()
                    prg.update(info)
                except Exception as e:
                    print(f"failure downloading s3://{f[1]}/{f[2]}: {str(e)}", file=sys.stderr)
            else:
                results_remain += [ f ]

        time.sleep(0.1)
        results = results_remain
        prg.print()

    print()
