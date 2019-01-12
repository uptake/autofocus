"""Download datasets
"""
import argparse
import logging
import time


def main():
    """TK

    Args: TK

    Returns: TK
    """
    pass


def _parse_args() -> dict:
    """Parse command-line arguments, and log them with level INFO.

    Also provides file docstring as description for --help/-h.

    Returns:
        Command-line argument names and values as keys and values of a
            Python dictionary
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', '-d', type=str, help='Dataset', default='2016_2017', choices=DATASETS)
    # parser.add_argument('bar',
    #                     nargs='*',
    #                     help='Variable-length positional argument',
    #                     )
    # parser.add_argument('--baz', action='store_true', help='Flag argument')
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
