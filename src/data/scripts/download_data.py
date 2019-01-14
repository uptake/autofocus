"""Download dataset
"""
import argparse
import logging
from pathlib import Path
import sys
import time


DATASETS = ['lpz_2016_2017', 'lpz_2012-2014', 'lpz_2018']


def main(dataset: str) -> None:
    if dataset == 'lpz_2016_2017':
        sys.path.insert(0, str(Path(__file__).parents[1]))
        from datasets import LPZData_2016_2017

        data = LPZData_2016_2017()
    else:
        raise NotImplementedError

    data.download()


def _parse_args() -> dict:
    """Parse command-line arguments, and log them with level INFO.

    Also provides file docstring as description for --help/-h.

    Returns:
        Command-line argument names and values as keys and values of a
            Python dictionary
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', '-d', type=str, help='Dataset', default='lpz_2016_2017', choices=DATASETS)
    args = vars(parser.parse_args())
    logging.info(f'Arguments passed at command line: {args}')
    return args


if __name__ == '__main__':
    start_time = time.time()
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s')
    logging.getLogger().setLevel(logging.INFO)
    args_dict = _parse_args()

    main(**args_dict)

    end_time = time.time()
    logging.info(f'Completed in {round(end_time - start_time, 2)} seconds')
