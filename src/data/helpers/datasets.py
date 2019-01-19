from dataclasses import dataclass
import logging
import os
from pathlib import Path
import sys
import tarfile
import threading
from tqdm import tqdm

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
                f'\rProgress: {self._seen_so_far} / {self._size}  ({percentage:.2f}%)'
            )
            sys.stdout.flush()


@dataclass
class Dataset:
    local_dir: Path

    def download(self):
        raise NotImplementedError

    def extract(self):
        raise NotImplementedError

    def process(self):
        raise NotImplementedError


@dataclass
class S3Dataset(Dataset):
    s3_bucket: str
    s3_key: str

    def __post_init__(self):
        self.local_archive_path = self.local_dir / os.path.basename(self.s3_key)

    def download(self):
        logging.info(f'Downloading {self.s3_key} to {self.local_archive_path}')
        self._seen_so_far = 0

        if not self.local_dir.is_dir():
            os.makedirs(self.local_dir)

        s3_client = boto3.resource('s3')

        progress = DownloadProgressPercentage(s3_client, self.s3_bucket, self.s3_key)

        try:
            s3_client.Bucket(self.s3_bucket).download_file(
                Key=self.s3_key,
                Filename=str(self.local_archive_path),
                Callback=progress,
            )
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise

    def extract(self):
        if not os.path.isfile(self.local_archive_path):
            raise FileNotFoundError(
                f'Dataset archive is not available at {self.local_archive_path}.'
                f'Run `download` method before `extract`.'
            )
        else:
            with tarfile.open(self.local_archive_path) as archive:
                members = archive.getmembers()
                for item in tqdm(iterable=members, total=len(members)):
                    archive.extract(member=item)


lpz_data_2016_2017_raw = S3Dataset(
    local_dir=DATA_DIR/'lpz',
    s3_bucket='autofocus',
    s3_key='lpz_data/data_2016_2017.tar.gz',
)