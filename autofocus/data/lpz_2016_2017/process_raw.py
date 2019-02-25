"""Process raw data"""
from functools import partial
import logging
import time

from creevey import Pipeline
from creevey.load_funcs.image import load_image
from creevey.ops.image import resize
from creevey.path_funcs import replace_dir
from creevey.util.image import find_image_files
from creevey.write_funcs.image import write_image

from autofocus.data.constants import DATA_DIR

MIN_DIM = 512
N_JOBS = 10
NUM_PIXELS_TO_TRIM = 198
THIS_DATASET_DIR = DATA_DIR / "lpz_2016_2017"
INDIR = THIS_DATASET_DIR / "raw" / "data_2016_2017"
OUTDIR = THIS_DATASET_DIR / "processed" / "images"


def main():
    # Bottom 198 pixels are often a footer of camera information. I
    # suspect that those pixels are more likely to lead the model to
    # learn batch effects that do not generalize than to lead to genuine
    # learning, so I remove them.
    trim_bottom = lambda image: image[:-NUM_PIXELS_TO_TRIM, :]
    resize_512 = partial(resize, min_dim=MIN_DIM)
    trim_resize_pipeline = Pipeline(
        load_func=load_image, ops=[trim_bottom, resize_512], write_func=write_image
    )

    image_paths = find_image_files(INDIR)
    path_func = partial(replace_dir, outdir=OUTDIR)

    logging.info(f"Processing images and writing results to {OUTDIR}")
    trim_resize_pipeline.run(
        inpaths=image_paths,
        path_func=path_func,
        n_jobs=N_JOBS,
        skip_existing=True,
        exceptions_to_catch=ZeroDivisionError,
    )


if __name__ == "__main__":
    start_time = time.time()
    logging.basicConfig(format="%(levelname)s %(asctime)s %(message)s")
    logging.getLogger().setLevel(logging.INFO)

    main()

    end_time = time.time()
    logging.info(f"Completed in {round(end_time - start_time, 2)} seconds")
