from collections import defaultdict
import logging
import os
from pathlib import Path
import sys
import tarfile
import threading
from tqdm import tqdm
from typing import Type

import boto3
import botocore


REPO_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_DIR / "data"


class _Dataset:
    def download(self):
        raise NotImplementedError

    def extract(self):
        raise NotImplementedError

    def process(self):
        raise NotImplementedError


class S3Dataset:
    def __init__(
        self,
        S3Downloader: Type["S3Downloader"],
        Extractor: Type["_Extractor"],
        Processor: Type["_Processor"],
        s3_bucket: str,
        s3_key: str,
        local_dir: Path,
    ):
        self.local_dir = local_dir
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key

        self.downloader = S3Downloader(
            s3_bucket=self.s3_bucket, s3_key=self.s3_key, local_dir=self.local_dir
        )
        self.extractor = Extractor(archive_path=self.downloader.local_archive_path)
        self.processor = Processor(data_dir=self.local_dir)

        self.download = self.downloader.download
        self.extract = self.extractor.extract
        self.processor = self.processor.process


class _Downloader:
    def __init__(self):
        raise NotImplementedError

    def download(self, local_dir):
        raise NotImplementedError


class S3Downloader(_Downloader):
    def __init__(self, s3_bucket: str, s3_key: str, local_dir: Path) -> None:
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.local_dir = local_dir
        self.local_archive_path = self.local_dir / os.path.basename(self.s3_key)

    def download(self):
        logging.info(f"Downloading {self.s3_key} to {self.local_archive_path}")
        self._seen_so_far = 0

        if not self.local_dir.is_dir():
            os.makedirs(self.local_dir)

        s3_client = boto3.resource("s3")
        progress = DownloadProgressPercentage(s3_client, self.s3_bucket, self.s3_key)
        try:
            s3_client.Bucket(self.s3_bucket).download_file(
                Key=self.s3_key,
                Filename=str(self.local_archive_path),
                Callback=progress,
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print("The object does not exist.")
            else:
                raise


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
                f"\rProgress: {self._seen_so_far} / {self._size}  ({percentage:.2f}%)"
            )
            sys.stdout.flush()


class _Extractor:
    def __init__(self):
        raise NotImplementedError

    def extract(self):
        raise NotImplementedError


class TarfileExtractor(_Extractor):
    def __init__(self, archive_path: Path):
        self.archive_path = archive_path

    def extract(self):
        with tarfile.open(self.archive_path) as archive:
            members = archive.getmembers()
            for item in tqdm(iterable=members, total=len(members)):
                archive.extract(member=item, path=self.local_archive_path.parent)


class _Processor:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.raw_data_dir = self.data_dir / "raw"
        self.interim_data_dir = self.raw_data_dir.parent / "interim"
        self.processed_data_dir = self.raw_data_dir.parent / "processed"

    def process(self):
        self.process_images()
        self.process_labels()

    def process_images(self):
        raise NotImplementedError

    def process_labels(self):
        raise NotImplementedError


class LPZ_2016_2017_Processor(_Processor):
    def process(self, local_dir: Path):
        super().__init__(local_dir)
        self.process_images()
        self.process_labels()

    def process_images(self):
        pass

    def process_labels(self):
        raise NotImplementedError

        labels = self.load_label_dataframes()
        self._correct_filepaths(df=labels, image_dir=self.raw_data_dir / "images")
        discard_rows_where_file_is_missing(df=labels, path_col="filepath")
        labels = _get_dummies(labels, columns=["ShortName"])
        discard_duplicate_rows(labels)
        labels = _groupby(df=labels, field="filepath", aggregation_func=max)
        _add_image_properties(labels, image_properties)
        labels = _clean_label_columns(labels)


class LPZ_2016_2017_RawProcessor(LPZ_2016_2017_Processor):
    def process_images(self):
        raise NotImplementedError

        image_properties = defaultdict(list)
        image_paths = get_paths_with_extensions(self.raw_data_dir, extensions)
        for path in tqdm(image_paths):
            image = cv.imread(str(path))
            try:
                processed_image = _process_image(image)
            except (ZeroDivisionError, TypeError):
                logging.warning(f"Skipping {path}, which did not load properly.")
            else:
                outpath = abspath(path).replace(abspath(indir), abspath(outdir))
                _record_properties(processed_image, image_properties, path, outpath)
                save_image(processed_image, outpath)
        csv_outpath = Path(outdir) / "image_properties.csv"
        write_csv(pd.DataFrame(image_properties), csv_outpath)


lpz_data_2016_2017_raw = S3Dataset(
    S3Downloader=S3Downloader,
    Extractor=TarfileExtractor,
    Processor=LPZ_2016_2017_RawProcessor,
    s3_bucket="autofocus",
    s3_key="lpz_data/data_2016_2017.tar.gz",
    local_dir=DATA_DIR / "lpz",
)
