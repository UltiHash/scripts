#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 11:22:39 2024

@author: massi
"""

import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        prog='UH Stats',
        description='Statistics from UH cluster')

    parser.add_argument('-u', '--url', help='override default S3 endpoint',
        nargs=1, default='http://localhost:8080', dest='url')

    return parser.parse_args()

def get_effective_size(config):
    effective_size = 0
    print(f"Ultihash effective size is {effective_size} MB")
    return effective_size

if __name__ == "__main__":
    config = parse_args()
    
    get_effective_size(config)
    
