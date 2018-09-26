# Autofocus

This project seeks to make conservation organizations more efficient, primarily by automating the process of labeling images taken by motion-activated "camera traps" according to the kinds of animals that appear in them. See [this article](https://www.uptake.org/autofocus.html) for more information.

**Caveats:**

- Data-cleaning code is currently specific to a particular data set. We are aiming to generalize it over time.
- Computer vision currently uses a lightly modified version of a script from the Tensorflow project. We are aiming to adapt it to perform better specifically for identifying animals in images from motion-activated "camera traps" over time.

## Steps for Training a Camera Traps Model

### 1. preprocess_images.py

#### Example call

```bash
python autofocus/preprocess_images.py \
--indir sample_data/images --outdir results/preprocessed_images
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
python autofocus/clean_detections.py --detections sample_data/sample_detections.csv \
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
