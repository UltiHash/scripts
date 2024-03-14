#!/usr/bin/env python3

import argparse
import concurrent.futures
import boto3
import os
import pathlib
import sys
import tqdm

AWS_KEY_ID="key-id"
AWS_KEY_SECRET="secret"

def parse_args():
    parser = argparse.ArgumentParser(
        prog='UH upload',
        description='Uploading files to UH cluster')

    parser.add_argument('path', help='directory or file to upload',
        type=pathlib.Path, nargs='+')
    parser.add_argument('-u', '--url', help='override default S3 endpoint',
        nargs=1, default='http://localhost:8080', dest='url')
    parser.add_argument('-v', '--verbose', help='write additional information to stdout',
        action='store_true', dest='verbose')
    parser.add_argument('-B', '--bucket', help='upload all files to the given bucket',
        action='store')
    parser.add_argument('-j', '--jobs', help='number of concurrent jobs',
        action='store', default=8, type=int)

    return parser.parse_args()

class uploader:
    def __init__(self, config):
        self.threads = concurrent.futures.ThreadPoolExecutor(max_workers=config.jobs)
        self.s3 = boto3.client('s3', endpoint_url=config.url[0],
            aws_access_key_id=AWS_KEY_ID, aws_secret_access_key=AWS_KEY_SECRET)
        self.progress = None
        self.count_buffer = 0

    def upload(self, path, bucket):
        def cb(count):
            if self.progress is not None:
                self.progress.update(count)
            else:
                self.count_buffer += count

        self.s3.upload_file(path, Bucket=bucket, Key=path.name, Callback=cb)

    def mk_bucket(self, bucket):
        self.s3.create_bucket(Bucket=bucket)

    def push(self, bucket, path):
        return self.threads.submit(self.upload, bucket, path)

    def set_total(self, total):
        self.progress = tqdm.tqdm(unit='b', unit_scale=True, total=total)
        self.progress.update(self.count_buffer)
        self.count_buffer = 0


if __name__ == "__main__":
    config = parse_args()

    up = uploader(config)
    results = []
    size_total = 0

    for path in config.path:
        path = path.resolve()

        if config.bucket is not None:
            bucket = config.bucket
        else:
            bucket = path.name

        print(f"\ruploading {path} to bucket {bucket}", end="")

        up.mk_bucket(bucket)

        for (root, dirs, files) in os.walk(path):
            for file in files:
                fullpath = pathlib.Path(root) / file
                size_total += fullpath.stat().st_size
                results += [(fullpath, up.push(fullpath, bucket))]

    up.set_total(size_total)

    for job in results:
        try:
            job[1].result()
        except Exception as e:
            print(f"Error uploading {job[0]}: {str(e)}", file=sys.stderr)

    print()
