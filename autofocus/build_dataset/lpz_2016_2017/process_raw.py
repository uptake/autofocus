"""Process raw data"""
from functools import partial
import logging
import os
from pathlib import Path
import time

from creevey import CustomReportingPipeline
from creevey.load_funcs.image import load_image
from creevey.ops.image import resize
from creevey.path_funcs import replace_dir
from creevey.util.image import find_image_files
from creevey.write_funcs.image import write_image
from fastai.vision import verify_images
import pandas as pd

from autofocus.build_dataset.constants import DATA_DIR
from autofocus.build_dataset.lpz_2016_2017.ops import (
    record_is_grayscale,
    record_mean_brightness,
    trim_bottom,
)

MIN_DIM = 512
N_JOBS = 5
NUM_PIXELS_TO_TRIM = 198

THIS_DATASET_DIR = DATA_DIR / "lpz_2016_2017"
RAW_DIR = THIS_DATASET_DIR / "raw" / "data_2016_2017"
RAW_CSV_FILENAMES = ["detections_2016.csv", "detections_2017.csv"]
RAW_CSV_PATHS = [RAW_DIR / fn for fn in RAW_CSV_FILENAMES]

PROCESSED_DIR = THIS_DATASET_DIR / "processed"
PROCESSED_IMAGE_DIR = PROCESSED_DIR / "images"
PROCESSED_LABELS_CSV_OUTPATH = PROCESSED_DIR / "labels.csv"

CORRUPTED_FILES = [
    RAW_DIR / "images_2016" / "DPT" / "D03-AMP1" / "._CHIL - D03-AMP1-JU16_00037.JPG"
]


def main():
    logging.info("Deleting known corrupted files")
    for path in CORRUPTED_FILES:
        path.unlink()
    logging.info(f"Processing images and writing results to {PROCESSED_IMAGE_DIR}")
    run_record = _process_images()
    logging.info("Processing labels")
    labels = _process_labels(run_record)
    logging.info(f"Writing processed labels to {PROCESSED_LABELS_CSV_OUTPATH }")
    labels.to_csv(PROCESSED_DIR / "labels.csv", index=False)


def _process_images():
    # Bottom 198 pixels are often a footer of camera information. I
    # suspect that those pixels are more likely to lead the model to
    # learn batch effects that do not generalize than to lead to genuine
    # learning, so I remove them.
    trim_footer = partial(trim_bottom, num_pixels=NUM_PIXELS_TO_TRIM)
    resize_min_dim = partial(resize, min_dim=MIN_DIM)
    ops = [trim_footer, resize_min_dim, record_is_grayscale, record_mean_brightness]

    trim_resize_pipeline = CustomReportingPipeline(
        load_func=load_image, ops=ops, write_func=write_image
    )

    image_paths = find_image_files(RAW_DIR)[:10]
    path_func = partial(replace_dir, outdir=PROCESSED_IMAGE_DIR)

    run_record = trim_resize_pipeline.run(
        inpaths=image_paths,
        path_func=path_func,
        n_jobs=N_JOBS,
        skip_existing=False,
        exceptions_to_catch=ZeroDivisionError,
    )
    logging.info("Checking for additional corrupted images")
    run_record = _delete_bad_images(run_record)

    return run_record


def _delete_bad_images(run_record):
    verify_images(PROCESSED_IMAGE_DIR, delete=True)
    is_file = run_record.loc[:, "outpath"].apply(os.path.isfile)
    run_record = run_record.loc[is_file, :]

    return run_record


def _process_labels(run_record):
    raw_df = (
        pd.concat([pd.read_csv(path) for path in RAW_CSV_PATHS], sort=False)
        .set_index("FileName")
        .drop(["Unnamed: 0", "FilePath"], axis="columns")
        .rename(columns={"ShortName": "label", "ImageDate": "date"})
    )

    run_record.index = pd.Series(run_record.index).apply(lambda path: Path(path).name)

    processed_df = (
        run_record.drop(
            ["skipped_existing", "exception_handled", "time_finished"], axis="columns"
        )
        .join(raw_df, how="left")
        .loc[:, ["outpath", "label", "grayscale", "mean_brightness", "date"]]
        .reset_index(drop=True)
    )
    processed_df.loc[:, "filename"] = processed_df.loc[:, "outpath"].apply(
        lambda path: Path(path).name
    )
    processed_df.loc[:, "location"] = processed_df.loc[:, "filename"].apply(
        lambda fn: fn.split("-")[2]
    )
    processed_df = processed_df.drop("outpath", axis="columns")

    return processed_df


if __name__ == "__main__":
    start_time = time.time()
    logging.basicConfig(format="%(levelname)s %(asctime)s %(message)s")
    logging.getLogger().setLevel(logging.INFO)

    main()

    end_time = time.time()
    logging.info(f"Completed in {round(end_time - start_time, 2)} seconds")
