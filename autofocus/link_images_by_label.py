"""Create symlinks to images grouped by label.
"""
import argparse
import json
import logging
import os
import psutil
import time

from pathlib import Path
from typing import Dict, List, Set

import pandas as pd

from tqdm import tqdm

from autofocus.util import discard_duplicate_rows


def main(detections_path: str,
         outdir: str,
         labelmap_path: str=None,
         label_priority_path: str=None,
         keep_unresolved: bool=False,
         ):
    detections = pd.read_csv(detections_path)
    labelmap = _create_labelmap(labelmap_path, detections)
    detections = _apply_labelmap(detections, labelmap)
    discard_duplicate_rows(detections)
    detections = _resolve_multilabel_cases(detections,
                                           label_priority_path,
                                           keep_unresolved,
                                           )
    _create_links(detections, labelmap, outdir)


def _get_label_colnames(detections):
    return [col for col in detections.columns if col.startswith('contains_')]


def _create_labelmap(labelmap_path: str, detections: pd.DataFrame) -> dict:
    """If labelmap_path is not None, load provided labelmap into a
    `dict`. Map any unmapped labels to themselves.
    """
    label_colnames = _get_label_colnames(detections)
    if labelmap_path is not None:
        with open(labelmap_path, 'r') as f:
            labelmap = json.load(f)
    else:
        labelmap = {}
    _create_trivial_mappings(labelmap, label_colnames)
    return labelmap


def _create_trivial_mappings(labelmap: Dict[str, str], label_colnames: List[str]) -> None:
    df_labels = [colname.replace('contains_', '') for colname in label_colnames]
    for label in df_labels:
        if label not in labelmap:
            logging.warning('No label mapping was provided for {label}, so it '
                            'will be kept unchanged.')
            labelmap[label] = label


def _apply_labelmap(detections: pd.DataFrame, labelmap: dict) -> pd.DataFrame:
    """Update the names of the label columns in `detections` according
    to `labelmap`.

    When the labelmap gives more than one input column the same name,
    collapse those columns by taking their max.
    """
    colmap = {f'contains_{key}': f'contains_{labelmap[key]}' for key in labelmap}
    detections.rename(columns=colmap, inplace=True)
    label_colnames = _get_label_colnames(detections)
    detections = _collapse_matching_label_cols(detections, label_colnames)
    return detections


def _collapse_matching_label_cols(detections: pd.DataFrame, label_colnames: List[str]) -> pd.DataFrame:
    is_label_col = detections.columns.isin(label_colnames)

    # Pandas has a bug that causes NaNs to become zeros when performing
    # certain operations over a groupby in many cases, including
    # apparently any case with string values
    # (https://github.com/pandas-dev/pandas/issues/20824).
    # The workaround here is to group and max only over the (integer)
    # label columns.
    specified_cols = detections.loc[:, is_label_col]
    other_cols = detections.loc[:, ~is_label_col]

    num_null_rows_before = specified_cols.isnull().sum(axis='columns')
    specified_cols = specified_cols.groupby(specified_cols.columns, axis='columns').max()
    num_null_rows_after = specified_cols.isnull().sum(axis='columns')

    detections = pd.concat([other_cols, specified_cols], axis='columns')
    if (num_null_rows_after != num_null_rows_before).any():
        raise AssertionError('Summing over columns eliminated some null '
                             'values. Confirm that label column values'
                             'are numeric.')
    return detections


def _resolve_multilabel_cases(detections: pd.DataFrame,
                              label_priority_path: str,
                              keep_unresolved: bool,
                              ) -> pd.DataFrame:
    """Discard detections in files with multiple detections according to
    `label_priority_rules` if `keep_unresolved` is False, discard any
    rows with multiple detections that remain.

    Args:
        label_priority_path: Path to a text file each row of which has
            the form "label1 > label2", where "label1" and "label2" are
            elements of `label_colnames`. "*" can be used to indicate
            "all other labels." For instance, "* > empty" indicates that
            all other labels have priority over "empty."
    """
    label_colnames = _get_label_colnames(detections)
    labels = [colname.replace('contains_', '') for colname in label_colnames]
    if label_priority_path is not None:
        priority_rules = _parse_priority_file(label_priority_path, labels)
        detections = _apply_priority_rules(detections, priority_rules)
    if keep_unresolved:
        pass
    else:
        has_multiple_labels = detections.loc[:, label_colnames].sum(axis='columns') > 1
        num_unresolved = sum(has_multiple_labels)
        if num_unresolved > 0:
            logging.warning(f'{num_unresolved} images have multiple labels and '
                            f'are being dropped')
        detections = detections.loc[~has_multiple_labels, :]
    return detections


def _parse_priority_file(label_priority_path: str, labels: List[str]) -> Dict[Set[str], str]:
    """
    Args:
        labels: The full set of labels in the dataset.

    Returns:
        Dict whose keys are two-member `frozenset` objects of label
            strings and whose corresponding values indicate which of
            those strings have priority.
    """
    priority_rules = {}
    with open(label_priority_path, 'r') as f:
        for line in f:
            label1, label2 = line.split(' > ')
            label1, label2 = map(lambda string: string.strip(), (label1, label2))
            _add_priority_rule(priority_rules, label1, label2, labels)
    return priority_rules


def _add_priority_rule(priority_rules: Dict[Set[str], str],
                       label1: str,
                       label2: str,
                       all_labels: List[str]
                       ) -> None:
    """Add a rule that `label1` supersedes `label2` to the
    `priority_rules` dictionary.

    Each priority rule has the form
    `{frozenset({label1, label2}): label1}`, indicating that `label1`
    has priority over `label2`. If `label1` is "*", then a rule is
    created for every label in `all_labels` except `label2` giving it
    priority over `label2`. If `label2` is "*", then a rule is created
    for every label in `all_labels` except `label1` giving `label1`
    priority over that label.

    Raises: ValueError if `priority_rules` already contains a rule for
        `label1` and `label2`.
    """
    _validate_labels(label1, label2, all_labels)
    if label1 == '*':
        for wildcard_label in all_labels:
            if wildcard_label != label2:
                _add_priority_rule(priority_rules, wildcard_label, label2, all_labels)
    elif label2 == '*':
        for wildcard_label in all_labels:
            if wildcard_label != label1:
                _add_priority_rule(priority_rules, label1, wildcard_label, all_labels)
    else:
        labelset = frozenset([label1, label2])
        if labelset in priority_rules:
            raise ValueError(f'Multiple priority rules provided for label pair '
                             f'{label1, label2}')
        else:
            priority_rules[labelset] = label1


def _validate_labels(label1: str, label2: str, all_labels: List[str]) -> None:
    for label in label1, label2:
        if label != '*' and label not in all_labels:
            logging.warning(f'Label {label} in priority rules is not in the dataset')
    if label1 == label2:
        raise ValueError(f'Invalid rule {label1} > {label2} in priority rules: '
                         f'all_labels must be distinct'
                         )


def _apply_priority_rules(df: pd.DataFrame, rules: Dict[Set[str], str]) -> pd.DataFrame:
    """Set detection columns to 0 where they conflict with
    higher-priority detection columns.
    """
    for labelset in rules:
        label1, label2 = labelset
        if f'contains_{label1}' in df.columns and f'contains_{label2}' in df.columns:
            row_is_relevant = (
                (df.loc[:, f'contains_{label1}'] == 1)
                & (df.loc[:, f'contains_{label2}'] == 1)
                )
            if row_is_relevant.any():
                if rules[labelset] == label1:
                    logging.warning(f'label {label2} conflicted with {label1} '
                                    f'and is being dropped from the following '
                                    f'rows: {df.loc[row_is_relevant]}'
                                    )
                    df.loc[row_is_relevant, f'contains_{label2}'] == 0
                else:
                    logging.warning(f'label {label1} conflicted with {label2} '
                                    f'and is being dropped from the following '
                                    f'rows: {df.loc[row_is_relevant]}')
                    df.loc[row_is_relevant, f'contains_{label1}'] == 0
        else:
            pass
    return df


def _create_links(df: pd.DataFrame, labelmap: Dict[str, str], outdir: str) -> None:
    """For every label in the labelmap values, create a directory
    within `outdir` containing symlinks to all images in `df` that have
    that label.
    """
    if os.path.isdir(outdir):
        raise ValueError(f'Output directory {outdir} already exists.')
    for label in set(labelmap.values()):
        linkdir_path = Path(outdir) / label
        _create_linkdir(df, label, linkdir_path)


def _create_linkdir(df: pd.DataFrame, label: str, linkdir_path: Path) -> None:
    colname = 'contains_' + label
    if colname in df.columns:
        if not os.path.exists(linkdir_path):
            os.makedirs(linkdir_path)
        df = df.loc[df.loc[:, colname] == 1, :]
        logging.info(f'Creating {len(df)} links for label {label} in {linkdir_path}')
        if len(df) > 0:
            df.progress_apply(lambda row: _create_single_link(row, linkdir_path), axis=1)


def _create_single_link(row: pd.Series, linkdir_path: Path) -> None:
    filename = os.path.basename(row.loc['filepath'])
    link_path = linkdir_path / filename
    os.symlink(row.loc['filepath'], link_path)


def _parse_args() -> dict:
    """Parse command-line arguments, and log them with level INFO.

    Also provides file docstring as description for --help/-h.

    Returns:
        Command-line argument names and values as keys and values of a
            Python dictionary
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--detections-path',
                        '-d',
                        type=str,
                        required=True,
                        help='Path to input CSV detections file'
                        )
    parser.add_argument('--labelmap-path',
                        '-m',
                        type=str,
                        required=False,
                        help='Path to input JSON labelmap file'
                        )
    parser.add_argument('--outdir',
                        '-o',
                        type=str,
                        required=True,
                        help='Path to desired output directory'
                        )
    parser.add_argument('--label-priority-path',
                        '-p',
                        type=str,
                        required=False,
                        help='Path to text file that specifies how to resolve '
                             'cases with multiple labels'
                        )
    parser.add_argument('--keep-unresolved',
                        action='store_true',
                        required=False,
                        default=False,
                        help='Flag to keep cases that still have multiple '
                             'labels after applying resolution rules.'
                        )
    args = vars(parser.parse_args())
    logging.info(f'Arguments passed at command line: {args}')
    return args


def _log_memory() -> None:
    memory = psutil.virtual_memory()
    logging.info(f'Memory total:  {_convert_to_gb(memory.total)} GB')
    logging.info(f'Memory used:  {_convert_to_gb(memory.used)} GB')
    logging.info(f'Memory available:  {_convert_to_gb(memory.available)} GB')


def _convert_to_gb(bytes: float) -> float:
    return round(bytes / (2 ** 30), 2)


if __name__ == '__main__':
    start_time = time.time()
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s')
    logging.getLogger().setLevel(logging.INFO)
    args_dict = _parse_args()
    _log_memory()

    tqdm.pandas()

    main(**args_dict)

    _log_memory()
    end_time = time.time()
    logging.info(f'Completed in {round(end_time - start_time, 2)} seconds')
