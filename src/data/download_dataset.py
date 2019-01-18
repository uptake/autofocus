"""Download dataset"""
import argparse
import logging
import time

from helpers.datasets import DATASETS


def main(dataset: str) -> None:
    if dataset == 'lpz_2016_2017':
        from helpers.datasets import lpz_data_2016_2017

        data = lpz_data_2016_2017
    else:
        raise NotImplementedError

    logging.info(f'Downloading {dataset} to {data.local_archive_path}')
    data.download()

    logging.info(f'Extracting dataset to {data.local_archive_path.parent}')
    data.extract()


def _parse_args() -> dict:
    """Parse command-line arguments, and log them with level INFO.

    Also provides file docstring as description for --help/-h.

    Returns:
        Command-line argument names and values as keys and values of a
            Python dictionary
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset',
                        nargs='?',
                        type=str,
                        default='lpz_2016_2017',
                        choices=DATASETS
                        )
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
