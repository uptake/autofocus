from creevey.datasets import _Processor, S3TarfileDataset


REPO_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_DIR / "data"


lpz_data_2016_2017_raw = S3TarfileDataset(
    Processor=LPZ_2016_2017_RawProcessor,
    s3_bucket="autofocus",
    s3_key="lpz_data/data_2016_2017.tar.gz",
    local_dir=DATA_DIR / "lpz",
)


class LPZ_2016_2017_RawProcessor(LPZ_2016_2017_Processor):
    def process_images(self):
        raise NotImplementedError

        image_properties = defaultdict(list)
        image_paths = get_paths_with_extensions(self.raw_data_dir, extensions)
        for path in tqdm(image_paths):
            image = cv.imread(str(path))
            try:
                processed_image = _process_image(image)
            except (ZeroDivisionError, TypeError):
                logging.warning(f"Skipping {path}, which did not load properly.")
            else:
                outpath = abspath(path).replace(abspath(indir), abspath(outdir))
                _record_properties(processed_image, image_properties, path, outpath)
                save_image(processed_image, outpath)
        csv_outpath = Path(outdir) / "image_properties.csv"
        write_csv(pd.DataFrame(image_properties), csv_outpath)


# class LPZ_2016_2017_Processor(_Processor):
#     def process(self, local_dir: Path):
#         super().__init__(local_dir)
#         self.process_images()
#         self.process_labels()
#
#     def process_images(self):
#         pass
#
#     def process_labels(self):
#         raise NotImplementedError
#
#         labels = self.load_label_dataframes()
#         self._correct_filepaths(df=labels, image_dir=self.raw_data_dir / "images")
#         discard_rows_where_file_is_missing(df=labels, path_col="filepath")
#         labels = _get_dummies(labels, columns=["ShortName"])
#         discard_duplicate_rows(labels)
#         labels = _groupby(df=labels, field="filepath", aggregation_func=max)
#         _add_image_properties(labels, image_properties)
#         labels = _clean_label_columns(labels)
#
