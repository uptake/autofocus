"""Do all steps to download and preprocess dataset"""
import argparse
import logging

from helpers.util import run_script


def main(dataset: str, raw: bool) -> None:
    if dataset == "lpz_2016_2017" and raw:
        from helpers.datasets import lpz_data_2016_2017_raw as data
    else:
        raise NotImplementedError(f"{dataset} has not been implemented.")
    data.get_raw()
    data.process()


def _parse_args() -> dict:
    """Parse command-line arguments, and log them with level INFO.

    Also provides file docstring as description for --help/-h.

    Returns:
        Command-line argument names and values as keys and values of a
            Python dictionary
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", nargs="?", type=str, default="lpz_2016_2017")
    parser.add_argument("--raw", action="store_true")
    args = vars(parser.parse_args())
    logging.info(f"Arguments passed at command line: {args}")
    return args


if __name__ == "__main__":
    run_script(_parse_args, main)
