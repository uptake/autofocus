import logging
import os
import psutil

import pandas as pd


<<<<<<< HEAD:src/data/util.py
def add_dataset


def write_csv(df: pd.DataFrame, outpath) -> None:
    """Write a DataFrame to CSV, creating the output directory if
    necessary.
=======
def _convert_to_gb(bytes: float) -> float:
    return round(bytes / (2**30), 2)
>>>>>>> 7195b78de5ad7b182d2e685215ed6a5d6029dc5c:src/data/util.py


def _log_memory() -> None:
    memory = psutil.virtual_memory()
    logging.info(f'Memory total:  {_convert_to_gb(memory.total)} GB')
    logging.info(f'Memory used:  {_convert_to_gb(memory.used)} GB')
    logging.info(f'Memory available:  {_convert_to_gb(memory.available)} GB')


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
