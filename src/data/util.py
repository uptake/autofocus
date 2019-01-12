import logging
import os

import pandas as pd


def add_dataset


def write_csv(df: pd.DataFrame, outpath) -> None:
    """Write a DataFrame to CSV, creating the output directory if
    necessary.

    Log the output path and number of rows.
    """
    logging.info('Writing detection records to disk')
    outdir = os.path.split(outpath)[0]
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    df.to_csv(outpath, index=False)
    logging.info(f'{len(df)} records written to {outpath}')


def discard_duplicate_rows(df: pd.DataFrame) -> None:
    """Discard duplicate rows from the input DataFrame in-place.

    Log a warning with the number of duplicates found, if not zero.
    """
    logging.info('Discarding duplicate rows')
    num_rows_before = len(df)
    df.drop_duplicates(inplace=True)
    num_rows_after = len(df)
    num_dups_found = num_rows_before - num_rows_after
    if num_dups_found > 0:
        logging.warning(f'{num_dups_found} duplicate records discarded.')
