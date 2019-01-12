"""Preprocess detection files and images.
"""
import argparse
import logging
import os
import time

from datetime import datetime
from typing import List

import pandas as pd
import psutil

from tqdm import tqdm

from autofocus.util import discard_duplicate_rows, write_csv


def main(detections: List[str], image_dir: str, image_properties: str, outpath: str, ) -> None:
    detections = _load_dataframes(detections)
    detections = _correct_filepaths(detections, image_dir)
    detections = discard_missing_files(detections, 'filepath')
    detections = _get_dummies(detections, columns=['ShortName'])
    discard_duplicate_rows(detections)
    detections = _groupby(detections, field='filepath', aggregation_func=max)
    detections = _add_image_properties(detections, image_properties)
    detections = _clean_detection_columns(detections)
    write_csv(detections, outpath)


def _load_dataframes(dataframe_paths: List[str]) -> pd.DataFrame:
    logging.info('Loading dataframes')
    df_list = [pd.read_csv(path) for path in dataframe_paths]
    df = pd.concat(df_list, sort=False)
    logging.info(f'{len(df)} records found')
    return df


def _correct_filepaths(detections: pd.DataFrame, image_dir: str) -> pd.DataFrame:
    logging.info('Correcting filepaths')
    detections.loc[:, 'filepath'] = (
        detections.progress_apply(lambda row: _get_filepath(row, image_dir), axis=1)
    )
    detections.drop('FilePath', axis='columns', inplace=True)
    return detections


def _get_filepath(row: pd.Series, image_dir: str) -> str:
    """Get local filepaths for a row in the detections DataFrame.

    CSV files from Lincoln Park Zoo give directory paths for their local
    machine, e.g. Z:\TransectTrailCamPics\SU16\DPT\D09-RYW1\. This
    function replaces the first two path elements
    (Z:\TransectTrailCamPics) with the provided image_dir and joins
    the result with the filename, to give a complete path on the user's
    local machine.
    """
    input_dirpath = row['FilePath']
    filename = row['FileName']
    original_dirpath_parts = input_dirpath.split('\\')
    dirpath_parts_to_keep = original_dirpath_parts[2:]

    return os.path.abspath(os.path.join(image_dir, *dirpath_parts_to_keep, filename))


def discard_missing_files(df: pd.DataFrame, path_colname: str) -> pd.DataFrame:
    """Discard rows where the indicated file does not exist or has
    filesize 0.

    Log a warning with the number of rows discarded, if not zero.

    Args:
        df
        path_colname: Name of `df` column that specifies paths to check
    """
    logging.info('Discarding missing files')
    nrows_before = len(df)
    file_exists = df.loc[:, path_colname].progress_apply(
        lambda x: os.path.isfile(x) and os.path.getsize(x) > 0
    )
    nrows_after = file_exists.sum()

    if nrows_after < nrows_before:
        logging.warning(f'{nrows_before - nrows_after} records discarded '
                        f'because file does not exist or is empty.'
                        )

    return df.loc[file_exists, :]


def _get_dummies(df: pd.DataFrame, columns=['ShortName']) -> pd.DataFrame:
    logging.info(f'Dummy-coding columns beginning with {columns}')
    return pd.get_dummies(df, columns=['ShortName'])



def _groupby(df, field, aggregation_func):
    logging.info(f'Combining records by {field}')
    rows_before = len(df)
    df = df.groupby(field).agg(aggregation_func).reset_index()
    rows_after = len(df)

    rows_lost = rows_after - rows_before
    if rows_lost > 0:
        logging.warning(f'{rows_lost} records combined with other records for '
                        f'the same file.')

    return df


def _add_image_properties(detections, image_properties):
    logging.info('Preparing image properties')
    image_properties_df = pd.read_csv(image_properties)
    image_properties_df.loc[:, 'filepath'] = (
        image_properties_df.loc[:, 'filepath'].progress_apply(os.path.abspath)
    )
    logging.info('Merging image properties')
    detections = pd.merge(detections, image_properties_df)
    logging.info('Extracting acquisition times')
    detections.loc[:, 'time'] = detections.progress_apply(_extract_time, axis=1)
    return detections


def _extract_time(row: pd.Series) -> datetime.time:
    """Record the time in exif_timestamp if the date in exif_timestamp
    matches the date in ImageDate (suggesting that exif_timestamp is
    correct). Otherwise, do not record a time.
    """
    csv_timestamp = datetime.strptime(row['ImageDate'], '%d-%b-%y')
    exif_timestamp = datetime.strptime(row['exif_timestamp'], '%Y-%m-%d %H:%M:%S')
    if csv_timestamp.date() == exif_timestamp.date():
        time = exif_timestamp.time()
    else:
        time = None
        logging.warning(f'Date in image exif timestamp {exif_timestamp} '
                        f'does not match date in detection record '
                        f'{row["ImageDate"]}. Not using exif timestamp.'
                        )
    return time


def _clean_detection_columns(detections: pd.DataFrame) -> pd.DataFrame:
    logging.info('Cleaning columns of detection records')
    detections.drop('exif_timestamp', axis='columns', inplace=True)
    label_column_prefix = 'ShortName'
    label_colnames = [
        colname for colname in detections.columns if colname.startswith(label_column_prefix)
    ]
    new_colnames = ['time', 'night', 'mean_brightness']
    column_order = ['filepath', 'ImageDate'] + new_colnames + label_colnames
    detections = detections.loc[:, column_order]
    label_colname_map = {col: col.replace(label_column_prefix, 'contains')
                         for col in label_colnames
                         }
    detections.rename(columns=label_colname_map, inplace=True)
    detections.rename(columns={'ImageDate': 'date'}, inplace=True)
    return detections


def _parse_args() -> dict:
    """Parse command-line arguments, and log them with level INFO.

    Also provides file docstring as description for --help/-h.

    Returns:
        Command-line argument names and values as keys and values of a
            Python dictionary
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--detections',
                        type=str,
                        nargs='*',
                        required=True,
                        help='Paths to input CSVs of detection labels.'
                        )
    parser.add_argument('--image-dir',
                        type=str,
                        required=True,
                        help='Path to directory that recursively '
                             'contains preprocessed copies of the '
                             'images referred to in detections CSV.'
                        )
    parser.add_argument('--image-properties',
                        type=str,
                        required=False,
                        help='Path to CSV of image properties, with '
                             'field "filepath" with paths to the '
                             'preprocessed files in `image-dir`.'
                        )
    parser.add_argument('--outpath',
                        type=str,
                        required=True,
                        help='Desired path to output of cleaned detection '
                             'labels.'
                        )
    args = vars(parser.parse_args())
    logging.info(f'Arguments pass at command line: {args}')
    return args


def _log_memory() -> None:
    memory = psutil.virtual_memory()
    logging.info(f'Memory total:  {_convert_to_gb(memory.total)} GB')
    logging.info(f'Memory used:  {_convert_to_gb(memory.used)} GB')
    logging.info(f'Memory available:  {_convert_to_gb(memory.available)} GB')


def _convert_to_gb(bytes: float) -> float:
    return round(bytes / (2**30), 2)


if __name__ == '__main__':
    start_time = time.time()
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s')
    logging.getLogger().setLevel(logging.DEBUG)
    args_dict = _parse_args()
    _log_memory()

    tqdm.pandas()

    main(**args_dict)

    _log_memory()
    end_time = time.time()
    logging.info(f'Completed in {round(end_time - start_time, 2)} seconds')
