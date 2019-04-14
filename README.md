# Autofocus

This project seeks to make conservation organizations more efficient by automating the process of labeling images taken by motion-activated "camera traps" according to the kinds of animals that appear in them. See [this article](https://www.uptake.org/autofocus.html) for more information.

## Quickstart

Install the package in editable model with dev dependencies:

```bash
pip install -e ".[dev]"
```

Download a preprocessed version of our primary dataset to `autofocus/data/lpz_2016_2017/processed`:

```bash
python autofocus/build_dataset/lpz_2016_2017/get_processed.py
```

This dataset contains approximately 80,000 images and a CSV of labels and image metadata. It occupies about 20GB uncompressed, but you will need about 40GB free for the downloading and untarring process.

## Getting the Raw Data

`autofocus/data/lpz_2016_2017/get_processed.py` downloads images that have been preprocessed by trimming the bottom 198 pixels (which often contains a metadata footer that could only mislead a machine learning model) and labels that have been cleaned up and organized. This preprocessing is intended to be fairly conservative, but you can download the raw data by running this commmand:

```bash
python autofocus/build_dataset/lpz_2016_2017/get_raw.py
```

The raw data takes up about 60GB untarred, but will need to have about 100GB free to download the tarfile and untar it before the tarfile is deleted.

`autofocus/data/lpz_2016_2017/process_raw.py` contains the code that was used to generate the processed data from the raw data.
