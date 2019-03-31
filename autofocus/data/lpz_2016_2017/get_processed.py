"""Get processed data from the Lincoln Park Zoo from 2016 and 2017"""
import logging
import time

from autofocus.data.constants import DATA_DIR
from autofocus.data.helpers import download_s3, untar

BUCKET = "autofocus"
KEY = "lpz_data/lpz_2016_2017_processed.tar.gz"

LOCAL_FILENAME = "lpz_2016_2017"
DOWNLOAD_DEST = DATA_DIR / (LOCAL_FILENAME + "_processed.tar.gz")
UNTAR_DEST = DATA_DIR / LOCAL_FILENAME


def main():
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True)

    if DOWNLOAD_DEST.exists():
        logging.warning(f"Skipping download because {DOWNLOAD_DEST} exists.")
    elif UNTAR_DEST.exists():
        raise ValueError(f"Aborting because {UNTAR_DEST} exists.")
    else:
        download_s3(KEY, BUCKET, DOWNLOAD_DEST)

    untar(DOWNLOAD_DEST, UNTAR_DEST)
    logging.info(f"Deleting {DOWNLOAD_DEST}")
    DOWNLOAD_DEST.unlink()


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s %(asctime)s %(message)s")
    logging.getLogger().setLevel(logging.INFO)
    start_time = time.time()

    main()

    end_time = time.time()
    logging.info(f"Completed in {round(end_time - start_time, 2)} seconds")
