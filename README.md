# Autofocus

This project seeks to make conservation organizations more efficient by automating the process of labeling images taken by motion-activated "camera traps" according to the kinds of animals that appear in them. See [this article](https://www.uptake.org/autofocus.html) for more information.

## Datasets

We currently have three datasets created by the Lincoln Park Zoo's Urban Wildlife Institute using camera traps around the Chicago area:

- `lpz_2016_2017` comes from mid-summer 2016 and mid-summer 2017. The current code in this repository was written to work with this dataset.
- `lpz_2012-2014` comes from the years 2012-2014. Unlike `lpz_2016_2017`, it includes images from all seasons. However, we have not yet written code for working with it, and its labels may be less clean.
- `lpz_2018` comes from 2018. Unlike the other datasets, it contains three-image bursts taken close together in time. However, it does not come with any labels.

We are currently handling these data sets separately because they are not organized and labeled in the same ways. It might be possible to normalize them so that they can be used together, for instance to train a single model.

## Building the Datasets

Sample call:

```bash
python src/data/make_dataset.py lpz_2016_2017
```

You can use the Python script `src/data/make_dataset.py` to build the datasets. It takes a positional argument that specifies which dataset you want. For instance, the command `python src/data/make_dataset.py lpz_2016_2017` builds the dataset `lpz_2016_2017`. At this time, only `lpz_2016_2017` has been implemented.

For the sake of transparency and repreoducibility, we prefer to treat raw data as immutable and to run code to generate derived products, rather than providing the derived products directly. However, the image files are sufficiently large that this approach is inconvenient. `src/data/make_dataset.py` does download raw tabular data containing image paths and labels and some additional to `data/<dataset>/raw/labels.csv` and then runs code to generate derived products from it, placing intermediate outputs in `data/<dataset>/interim/` and final outputs in `data/<dataset/processed/`. However, to save time and user storage, by default it skips downloading the raw images and instead downloads to `data/<dataset>/processed/images` versions of the images that have already had a bottom strip of pixels that often contains a footer with camera information trimmed off and have been resized to 299 pixels along its smaller dimension. It also downloads metadata that has been derived from the original image files to `data/<dataset>/interim/image_metadata.csv`; this data gets joined with the raw tabular data to produce the tabular data in `data/<dataset/processed/`. Adding the `--raw` flag causes it to download and process the raw images instead.

## Customizing the Datasets for Modeling

Sample call:

```bash
python src/data/customize_labels.py --labelmap-path config/human_labelmap.json
```

`src/data/make_dataset.py` does not modify any of the labels in the tabular data we received from the Lincoln Park Zoo, but a user might wish to modify them before training a model for two main reasons.

First, at least in `lpz_2016_2017` small fraction of the images have more than one label. In some cases, these images actually show multiple types of animals that correspond to those labels; "human" and "dog" is a particularly common combination. In other cases, one of the labels is incorrect. For instance, it is somewhat common for an image to be labeled both with an animal species and with "empty," particularly if apparent signs of the animal are ambiguous or difficult to spot.

Second, the labels are more fine-grained than might be necessary or feasible for automate. For instance, `lpz_2016_2017` has labels for multiple distinct species of squirrel. Distinguishing among these species might be difficult for a computer vision model and might be unnecessary for some projects. Indeed, some projects might only require a binary classifier; simply identifying which images contain humans, for instance, can help researchers interested in the animals avoid wasting time looking at human images.

The script `src/data/customize_labels.py` provides mechanisms for addressing both of these issues. To address the problem of multiply labeled images, it has an argument `--label-priority-path` that takes a path to a CSV  with columns "dominant" and "recessive." If, for instance, that file contains a row with "human" in the "dominant" column and "empty" in the recessive column, then for any images that have a row with a "human" label and a row with an "empty" label, the row with the "empty" label will be dropped. The wildcard symbol "\*" can be used to indicate that a label is dominant or recessive to all other labels. By default, `src/data/customize_labels.py` uses a file that has "\*" dominant over "empty" (assuming that the "empty" label is wrong when another label is present for the same image) and no other precedence relations. After applying these precedence relations, `src/data/customize_labels.py` by default drops all rows that point to images with multiple labels; the flag `--keep-unresolved` can be used to keep them instead, for instance to train a multilabel model.

To address label grain, `src/data/customize_labels.py` has an argument `labelmap-path` that takes a path to a JSON file that consists of a JSON object mapping input labels to output labels. By default it does no label mapping, but two sample files have been provided: `config/family_labelmap.json` maps each input label to roughly the corresponding taxonomic family, and `config/human_labelmap.json` maps "human" and variants of "lawn_mower" to "human" and everything else to "other."

`src/data/customize_labels.py` writes its output to `data/<dataset>/custom`. 

## Training a Model

Sample call:

```bash
python src/models/train_model.py data/lpz_2016_2016/labels.csv
```

`src/models/train_model.py` uses the fast.ai library to train a convolutional neural network, following standard practices recommended in the fast.ai course. It takes the path to a CSV of labels as its command-line argument. That CSV needs to have columns "path" and "label." If it has a column "group" then any raws with the same value in that column will be kept together when splitting the data into training and validation sets, for splitting on larger units than individual images, such as sites or image burst events.

This script has a parameter `--test-size` that can take either a decimal number between 0 and 1 to specify the proportion of items (groups if a "group" column is provided) to be used for validation or a number without a decimal to specify the number of items to be used for validation. By default, the script uses the smaller of one tenth of the items or 10,000 total items.

## Serving Model Predictions

`src/api` contains code for serving model predictions through an API. It includes its own README.


## Downloading the Raw Images

You can use `src/data/download_raw_dataset.py` to download the raw images that `src/data/make_dataset.py` bypasses.

Sample call:

```bash
python download_raw_images.py lpz_2016_2017
```

The first command-line argument to this sprint specifies the dataset. You can provide a second argument to specify the download directory; by default, the script uses `data/<dataset>/raw/images`.

WARNING: These datasets may be quite large.

### Processing the Raw Images

```bash
python src/data/preprocess_images.py
```

#### Inputs

- indir: directory that that recursively contains the image files of interest
- outdir: desired output directory
- extensions: extensions of image files within indir ("[JPG]" by default)

#### Output

`outdir` directory that contains `<outdir>/image_properties.csv` with fields "filepath", "date", "time", "night" (0 or 1), "mean brightness"; and trimmed, resized copies of every image in `indir` with one of the specified extensions, where the location of each image copy within `outdir` matches the location of the corresponding image within `indir`.

## Compatibility

This package was developed using Python 3.6.

---

### 2. clean_detections.py

#### Example call

```bash
python autofocus/clean_detections.py --detections data/lpz_data/detections_2016.csv \
--image-dir results/preprocessed_images \
--image-properties results/preprocessed_images/image_properties.csv \
--outpath results/detections_clean.csv
```

Concatenate the contents of the input detection files. Update the paths in those detection files to point to the preprocessed images in `image-dir`. Pull in the image properties from the CSV created in the previous step. Save the result.

#### Inputs

- detections: paths to one or more CSV files. Each file is assumed to have columns "ImageDate", "FilePath", "FileName", and "ShortName". The paths in "FilePath" are assumed to begin with two components when split in "\" which are to be replaced with `image_dir`.
- image-dir: path to directory created in the previous step.
- image-properties: path to CSV with a "filepath" field that points to the files in `image-dir` and provides additional image properties.
- outpath: desired output path

#### Output

CSV of cleaned-up detection records, with columns "date", "filepath", "time", "night", "mean_brightness", and one binary column "contains_<label>" for each value in the input "ShortName" column. A given image *may* have the value 1 for multiple label columns.  