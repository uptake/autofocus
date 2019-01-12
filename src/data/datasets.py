from pathlib import Path

import boto3


REPO_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_DIR/'data'

@dataclass
class Dataset:
    local_dir: Path

    def download(self):
        raise NotImplementedError


class LPZData_2015_2016(Dataset):
    def __init__(self):
        local_directory = DATA_DIR/'lpz'/'2015_2016'
        s3_bucket = 's3://autofocus'
        s3_path = 'lpz_data/data_2015_2016.tar.gz'
