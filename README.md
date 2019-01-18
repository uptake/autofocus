# Autofocus

This project seeks to make conservation organizations more efficient by automating the process of labeling images taken by motion-activated "camera traps" according to the kinds of animals that appear in them. See [this article](https://www.uptake.org/autofocus.html) for more information.

Data is being uploaded to `s3://autofocus`. Providing convenient ways to download a sample data set and the full data set from this location is a top priority.

## Datasets

We currently have three datasets created by the Lincoln Park Zoo's Urban Wildlife Institute using camera traps around the Chicago area:

- `data_2016_2017` comes from mid-summer 2016 and mid-summer 2017. The current code in this repository was written to work with this dataset.
- `data_2012-2014` comes from the years 2012-2014. Unlike `data_2016_2017`, it includes images from all seasons. However, we have not yet written code for working with it, and its labels may be less clean.
- `data_2018` comes from 2018. Unlike the other datasets, it contains three-image bursts taken close together in time. However, it does not come with any labels.

We are currently handling these data sets separately because they are not organized and labeled in the same ways. It might be possible to normalize them so that they can be used together, for instance to train a single model.

## Getting Started

### Building the Datasets

Sample call:

```bash
python src/data/make_dataset.py data_2016_2017
```

You can use the Python script `src/data/make_dataset.py` to build the datasets. It takes a positional argument that specifies which dataset you want. For instance, the command `python src/data/make_dataset.py data_2016_2017` builds the dataset `data_2016_2017`. At this time, only `data_2016_2017` has been implemented.

These datasets generally have two components: tabular data files with image paths and labels and additional metadata; and the images themselves. `src/data/make_dataset.py` downloads the raw tabular data files as we received them from the Lincoln Park Zoo to `data/<dataset>/raw/` and processed versions of those files to `data/<dataset>/processed`. If there is a need to write intermediate tabular data files to disk, it writes them to `data/<dataset>/interim/`. This processing is intended to be fairly minimal and lossless, but we believe in treating the raw files as immutable and using code to derive processed results from them for the sake of transparency and reproducibility. On the image side, however, the original files are large enough that downloading the raw files is generally more trouble than it is worth. To save time and user storage, `src/data/make_dataset.py` downloads to `data/processed/images versions of the images that have already had a bottom strip of pixels that often contains a footer with camera information trimmed off and have been resized to 299x299 pixels. 

The raw images are available for users who would like to work with them; see the section "Going Deeper" below for more information.

### Preparing the Datasets for Modeling

Sample call:

```bash
python src/data/customize_detections.py --labelmap-path config/human_labelmap.json
```

`src/data/make_dataset.py` does not modify any of the labels in the tabular data we received from the Lincoln Park Zoo, but a user might wish to modify them before training a model for two main reasons.

First, at least in `data_2016_2017` small fraction of the images have more than one label. In some cases, these images actually show multiple types of animals that correspond to those labels; "human" and "dog" is a particularly common combination. In other cases, one of the labels is incorrect. For instance, it is somewhat common for an image to be labeled both with an animal species and with "empty," particularly if apparent signs of the animal are ambiguous or difficult to spot.

Second, the labels are more fine-grained than might be necessary or feasible for automate. For instance, `data_2016_2017` has labels for multiple distinct species of squirrel. Distinguishing among these species might be difficult for a computer vision model and might be unnecessary for some projects. Indeed, some projects might only require a binary classifier; simply identifying which images contain humans, for instance, can help researchers interested in the animals avoid wasting time looking at human images.

The script `src/data/customize_detections.py` provides mechanisms for addressing both of these issues. To address the problem of multiply labeled images, it has an argument `--label-priority-path` that takes a path to a CSV  with columns "dominant" and "recessive." If, for instance, that file contains a row with "human" in the "dominant" column and "empty" in the recessive column, then for any images that have a row with a "human" label and a row with an "empty" label, the row with the "empty" label will be dropped. The wildcard symbol "\*" can be used to indicate that a label is dominant or recessive to all other labels. By default, `src/data/customize_detections.py` uses a file that has "\*" dominant over "empty" (assuming that the "empty" label is wrong when another label is present for the same image) and no other precedence relations. After applying these precedence relations, `src/data/customize_detections.py` by default drops all rows that point to images with multiple labels; the flag `--keep-unresolved` can be used to keep them instead, for instance to train a multilabel model.

To address label grain, `src/data/customize_detections.py` has an argument `labelmap-path` that takes a path to a JSON file that consists of a JSON object mapping input labels to output labels. By default it does no label mapping, but two sample files have been provided: `config/family_labelmap.json` maps each input label to roughly the corresponding taxonomic family, and `config/human_labelmap.json` maps "human" and variants of "lawn_mower" to "human" and everything else to "other."

`src/data/customize_detections.py` writes its output to `data/<dataset>/custom`. 

### Training a Model

Sample call:

```bash
python src/models/train_model.py --csv-path data/data_2016_2016/labels.csv
```

`src/models/train_model.py` uses the fast.ai library to train a convolutional neural network, following standard practices recommended in the fast.ai course. 

We plan to replace this code with code that uses modeling techniques more customized for camera traps images.

### Serving Model Predictions

`src/api` contains code for serving model predictions through an API, including its own README.

## Going Deeper

### Building the Datasets

The scripts described here provide access to the raw images and the steps we used to process the versions you receive when you run `src/data/make_dataset.py`.

1. download_images.py

#### Example call
```bash
python src/data/download_images.py \
--local_folder data --bucket autofocus
```

#### Details
Downloads all images from an S3 bucket and keeps subdirectory structure intact.
WARNING: This dataset is over 80 GB.

#### Inputs

- local-folder: path to save files to locally
- bucket: S3 bucket to copy locally
- download-tar: Flag of whether to download tar files. 

#### Output

`data` with files and structure copied from S3

### 1. preprocess_images.py

#### Example call

```bash
python autofocus/preprocess_images.py \
--indir data/lpz_data/images_2016 --outdir results/preprocessed_images
```

#### Details

Find every file that is recursively contained within `indir` with one of the specified extensions. For each of those files, open it and trim the bottom 198 rows of pixels, which often contains a footer with metadata about the camera and acquisition time. Resize the image so that the smaller of its width and height is 256 pixels, which is large enough for a typical imagenet-pretrained model. Record whether or not it was taken at night based on whether all the channels are the same. Also record the image's mean grayscale brightness so that it is easy to discard washed-out images downstream. (Any additional feature extraction for machine learning purposes should be done downstream -- this script is intended as a preprocessing step, not an analysis step.) Save the resulting image in `outdir`, mirroring the directory structure in `indir`. After all of the images have been processed, save the image paths and properties to `<outdir>/image_properties.csv`.

#### Inputs

- indir: directory that that recursively contains the image files of interest
- outdir: desired output directory
- extensions: extensions of image files within indir ("[JPG]" by default)

#### Output

`outdir` directory that contains `<outdir>/image_properties.csv` with fields "filepath", "date", "time", "night" (0 or 1), "mean brightness"; and trimmed, resized copies of every image in `indir` with one of the specified extensions, where the location of each image copy within `outdir` matches the location of the corresponding image within `indir`.

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

### 3. link_images_by_label.py

Create symlinks to images organized into subdirectories according to specified labelmap and conflict resolution rules.

#### Example call

```bash
python autofocus/link_images_by_label.py \
--detections-path results/detections_clean.csv \
--labelmap-path sample_data/raccoon_labelmap.json \
--label-priority-path sample_data/label_priority.txt --outdir results/raccoon_symlinks
```

#### Inputs

- detections: path to CSV with fields "filepath" that points to image files and "label" that gives associated labels.
- labelmap (optional): path to JSON file that maps labels used in input CSV labels to labels to be used for classification. For instance, one might wish to combine all but one of the input labels and train a binary classifier. Any labels present in the CSV at detections_path not contained in this file will be left unchanged.
- label-priority (optional): path to text file that specifies label priorities for files with multiple labels. Each line provides one label ordering in the format `a > b`, where a and b are labels that are expected to be present in the detections after applying the labelmap. For instance, `human > empty` means that if a file has both labels "human" and "empty", then the "empty" label should be discarded. The special symbol `*` can be used to indicate all other labels -- for instance `* > empty` indicates that "empty" should always be dropped when it is one of multiple labels. Note: these rules are applied in the order in which they are listed, which can make a difference if they contain cycles (e.g. "human > dog", "dog > empty", "empty > human").
- keep-unresolved (flag): By default, any files that have multiple labels after applying any priority rules specified in `label_priority_config_path` are ignored rather than being copied multiple times, so that a classification model can be appropriately applied. If the `keep-unresolved` flag is set, then they will be copied multiple times instead, which would be appropriate for developing multiple binary classifiers, e.g. with multitask learning.
- outdir: desired output directory

#### Output

Within `outdir`, creates one directory for each label in the dataset after applying the provided labelmap and label priority rules and dropping remaining files with multiple labels if keep-unresolved is not set. Creates symlinks within each of those directories for the corresponding files.

### 4. retrain.py

Retrain the classifier layer of an imagenet-trained convolutional neural network.

#### Example call

```
python autofocus/retrain.py --image_dir results/raccoon_symlinks
```

Run `autofocus/retrain.py -h` for documentation. Uses MLFlow for run tracking; run `mlflow ui` to see results.

## Compatibility

This package was developed using Python 3.6.

#### References

* [How to Retrain an Image Classifier for New Categories (Tensorflow)](https://www.tensorflow.org/hub/tutorials/image_retraining)
