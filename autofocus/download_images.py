import argparse
import logging
import os
import time

import boto3

from autofocus.util import _log_memory


def main(local_folder: str, bucket: str, download_tar: bool=False) -> None:
    """Download all files in an S3 bucket locally.

    Args:
        local: path to save files to locally
        bucket: S3 bucket to copy locally
        download_tar: Flag for whether or not to download tar files
    """
    client = boto3.client('s3')
    resource = boto3.resource('s3')
    download_s3_bucket(
        client=client,
        resource=resource,
        prefix='',
        local_folder=local_folder,
        bucket=bucket,
        download_tar=download_tar
    )


def download_s3_bucket(
    client,
    resource,
    prefix: str,
    local_folder: str,
    bucket: str,
    download_tar: bool=True
) -> None:
    """Download the contents of an S3 bucket, preserving the subfolder structure

    Args:
        client (boto3.client): boto3 S3 client
        resource (boto3.resource): boto3 S3 resource
        prefix: prefix of files in S3
        local_folder: path to save files to locally
        bucket: S3 bucket to copy locally
        download_tar: Flag for whether or not to download tar files
    """
    print('DOWNLOAD TAR: {}'.format(download_tar))
    paginator = client.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=prefix):
        if result.get('CommonPrefixes') is not None:
            for subdir in result.get('CommonPrefixes'):
                print('Current Prefix: {}'.format(subdir.get('Prefix')))
                download_s3_bucket(
                    client=client,
                    resource=resource,
                    prefix=subdir.get('Prefix'),
                    local_folder=local_folder,
                    bucket=bucket,
                    download_tar=download_tar
                )
        if result.get('Contents') is not None:
            for file in result.get('Contents'):
                key = file.get('Key')
                local_path = local_folder + os.sep + key
                if 'tar.gz' in key and not download_tar:
                    print('Skipping tar file: {}'.format(key))
                    pass
                if not os.path.exists(os.path.dirname(local_path)):
                    os.makedirs(os.path.dirname(local_path))
                resource.meta.client.download_file(bucket, key, local_path)


def _parse_args() -> dict:
    """Parse command-line arguments, and log them with level INFO.

    Also provides file docstring as description for --help/-h.

    Returns:
        Command-line argument names and values as keys and values of a
            Python dictionary
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-folder', '-l',
                        type=str,
                        required=True,
                        help='Path to local directory to save files to '
                        )
    parser.add_argument('--bucket', '-b',
                        type=str,
                        required=True,
                        help='s3 bucket to copy'
                        )
    parser.add_argument('--download-tar', '-t',
                        action='store_true',
                        required=False,
                        default=False,
                        help='Flag of whether or not to download tar files'
                        )
    args = vars(parser.parse_args())
    logging.info(f'Arguments pass at command line: {args}')
    return args


if __name__ == '__main__':
    start_time = time.time()
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s')
    logging.getLogger().setLevel(logging.INFO)
    args_dict = _parse_args()
    _log_memory()

    main(**args_dict)

    _log_memory()
    end_time = time.time()
    logging.info(f'Completed in {round(end_time - start_time, 2)} seconds')
