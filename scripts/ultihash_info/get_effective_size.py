#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 11:22:39 2024

@author: massi
"""

import argparse
import sys
sys.path.insert(1,'../../otel')
from otel_exporter import otel_exporter

def parse_args():
    parser = argparse.ArgumentParser(
        prog='UH Stats',
        description='Statistics from UH cluster')

    parser.add_argument('-u', '--url', help='override default S3 endpoint',
        nargs=1, default='http://localhost:8080', dest='url')
    parser.add_argument('--test-name', help='name of the test',
        nargs=1, default='unnamed', dest='test_name')
    parser.add_argument('--otel-url', help='open telemetry url',
        nargs=1, dest='otel_url')

    return parser.parse_args()

if __name__ == "__main__":
    config = parse_args()
    
    effective_size = 0
    
    if (config.otel_url):
        otel = otel_exporter(config.otel_url[0], config.test_name[0])
        otel.create_metric("effective_size")
        otel.push_value("effective_size", effective_size)
        
    print(f"Ultihash effective size is {effective_size} MB")