from boto3.s3.transfer import S3Transfer
from dataclasses import dataclass
import logging
import os
from pathlib import Path
import sys
import threading
from typing import Callable

import boto3
import botocore


REPO_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_DIR/'data'


class DownloadProgressPercentage:
    def __init__(self, client, bucket, key):
        self._key = key
        self._size = client.Bucket(bucket).Object(key).content_length
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._key, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


@dataclass
class Dataset:
    local_dir: Path

    def download(self):
        raise NotImplementedError


@dataclass
class S3Dataset(Dataset):
    s3_bucket: str
    s3_key: str
    s3: Callable

    def download(self):
        outpath = self.local_dir/os.path.basename(self.s3_key)
        self._seen_so_far = 0

        if not self.local_dir.is_dir():
            os.makedirs(self.local_dir)

        try:
            progress = DownloadProgressPercentage(self.s3, self.s3_bucket, self.s3_key)

            self.s3.Bucket(self.s3_bucket).download_file(
                Key=self.s3_key,
                Filename=str(outpath),
                Callback=progress,
            )
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise


class LPZData_2016_2017(S3Dataset):
    def __init__(self):
        self.local_dir = DATA_DIR/'lpz'
        self.s3_bucket = 'autofocus'
        self.s3_key = 'lpz_data/data_2016_2017.tar.gz'
        self.s3 = boto3.resource('s3')


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    data = LPZData_2016_2017()
    data.download()
