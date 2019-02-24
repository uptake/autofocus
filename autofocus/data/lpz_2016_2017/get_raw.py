"""Get raw data from the Lincoln Park Zoo from 2015 and 2016"""
import logging
from pathlib import Path

from autofocus.data.helpers import download_s3, untar

BUCKET = "autofocus"
KEY = "lpz_data/data_2016_2017.tar.gz"
REPO_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_DIR / "data"


def main():
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True)
    local_filename = "lpz_data_2016_2017"
    download_dest = DATA_DIR / (local_filename + ".tar.gz")
    untar_dest = DATA_DIR / local_filename / "raw"

    if download_dest.exists():
        logging.warning(f"Skipping download because {download_dest} exists.")
    elif untar_dest.exists():
        raise ValueError(f"Aborting because {untar_dest} exists.")
    else:
        download_s3(KEY, BUCKET, download_dest)

    untar(download_dest, untar_dest)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s %(asctime)s %(message)s")
    logging.getLogger().setLevel(logging.INFO)

    main()
