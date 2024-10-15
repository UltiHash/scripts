#!/usr/bin/env python3

import argparse
import concurrent.futures
import boto3
import boto3.s3.transfer
import botocore
import os
import pathlib
import sys
import time
import tqdm

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
    parser.add_argument('-C', '--connections', help='number of connections per job',
        action='store', default=10, type=int)
    parser.add_argument('--read-timeout', help='read timeout in seconds',
        action='store', default=60, type=int)
    parser.add_argument('--max-attempts', help='maximum number of upload attempts',
        action='store', default=3, type=int)
    parser.add_argument('--no-multipart', help='disable multipart upload entirely',
        action='store_true', dest='no_multipart')
    parser.add_argument('--multipart-chunksize', help='size of multipart upload chunks',
        action='store', default=8*1024*1024, type=int)
    parser.add_argument('-q', '--quiet', help='do not show progress bar',
        action='store_true', dest='quiet')

    return parser.parse_args()

class uploader:
    def __init__(self, config):
        self.threads = concurrent.futures.ThreadPoolExecutor(max_workers=config.jobs)

        s3_cnf = botocore.config.Config(
            read_timeout=config.read_timeout,
            retries = {
                'max_attempts': config.max_attempts,
                'mode': 'standard'
            })

        if config.no_multipart:
            self.transfer_config = boto3.s3.transfer.TransferConfig(
                multipart_threshold = 16 * 1024 * 1024 * 1024 * 1024,
                max_concurrency=config.connections)
        else:
            self.transfer_config = boto3.s3.transfer.TransferConfig(
                multipart_chunksize = config.multipart_chunksize,
                max_concurrency=config.connections)

        self.s3 = boto3.client('s3', endpoint_url=config.url[0], config=s3_cnf)
        self.progress = None
        self.count_buffer = 0
        self.quiet = config.quiet

    def upload(self, bucket, file_path, base_path):
        def cb(count):
            if self.progress is not None:
                self.progress.update(count)
            else:
                self.count_buffer += count
        self.s3.upload_file(file_path, Bucket=bucket, Key=str(file_path.relative_to(base_path)), Callback=cb, Config=self.transfer_config)

    def mk_bucket(self, bucket):
        self.s3.create_bucket(Bucket=bucket)

    def push(self, bucket, file_path, base_path):
        return self.threads.submit(self.upload, bucket, file_path, base_path)

    def stop(self):
        if self.progress is not None:
            self.progress.close()

    def set_total(self, total):
        if not self.quiet:
            self.progress = tqdm.tqdm(unit='B', unit_scale=True, total=total)
            self.progress.update(self.count_buffer)
            self.count_buffer = 0

def upload (config):
    up = uploader(config)
    results = []
    size_total = 0

    start = time.monotonic()

    for base_path in config.path:

        if config.bucket is not None:
            bucket = config.bucket
        else:
            bucket = base_path.name

        if not config.quiet:
            print(f"\ruploading {base_path} to bucket {bucket}", end="")

        try:
            up.mk_bucket(bucket)
        except:
            pass

        if base_path.is_file():
            results += [(base_path, up.push(bucket, base_path, pathlib.Path(base_path).parent))]
            size_total += base_path.stat().st_size
            continue

        for (root, dirs, files) in os.walk(base_path):
            for file in files:
                file_path = pathlib.Path(root) / file
                size_total += file_path.stat().st_size
                results += [(file_path, up.push(bucket, file_path, base_path))]

    up.set_total(size_total)

    for job in results:
        try:
            job[1].result()
        except Exception as e:
            print(f"Error uploading {job[0]}: {str(e)}", file=sys.stderr)

    end = time.monotonic()
    seconds = end - start
    mb = size_total / (1024 * 1024)

    up.stop()
    print(f"average upload speed: {mb/seconds} MB/s")

    return float(mb)/seconds

if __name__ == "__main__":
    config = parse_args()
    upload(config)



