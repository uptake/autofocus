import logging
from pathlib import Path
import tarfile
import threading
import sys
from typing import Union

import boto3
from tqdm import tqdm

PathOrStr = Union[Path, str]


def download_s3(key: str, bucket: str, dest: PathOrStr):
    logging.info(f"Downloading {key} to {dest}")

    outdir = Path(dest).parent

    if not outdir.exists():
        outdir.mkdir(parents=True)

    client = boto3.resource("s3")
    progress = S3DownloadProgressPercentage(client, bucket, key)
    client.Bucket(bucket).download_file(Key=key, Filename=str(dest), Callback=progress)
    print()  # add linebreak after progress percentage


def untar(inpath, outdir):
    logging.info(f"Untarring {inpath} to {outdir}")
    with tarfile.open(inpath) as archive:
        members = archive.getmembers()
        for item in tqdm(iterable=members, total=len(members)):
            archive.extract(member=item, path=outdir)


class S3DownloadProgressPercentage:
    """Use as a callback to track download progress."""

    def __init__(self, client, bucket, key):
        self._key = key
        self._size = client.Bucket(bucket).Object(key).content_length
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):  # noqa: 170
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                f"\rProgress: {self._seen_so_far} / {self._size}  ({percentage:.2f}%)"
            )
            sys.stdout.flush()
