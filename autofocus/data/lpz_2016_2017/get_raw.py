"""Get raw data from the Lincoln Park Zoo from 2015 and 2016"""
import logging
import time

from autofocus.data.constants import DATA_DIR
from autofocus.data.helpers import download_s3, untar

BUCKET = "autofocus"
KEY = "lpz_data/data_2016_2017.tar.gz"


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
    logging.info(f"Deleting {download_dest}")
    download_dest.unlink()


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s %(asctime)s %(message)s")
    logging.getLogger().setLevel(logging.INFO)
    start_time = time.time()

    main()

    end_time = time.time()
    logging.info(f"Completed in {round(end_time - start_time, 2)} seconds")
