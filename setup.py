from pathlib import Path
from setuptools import find_packages, setup

THIS_FILE_DIR = Path(__file__).resolve().parent
VERSION_FILE_PATH = THIS_FILE_DIR / "autofocus" / "_version.py"
README_FILE_PATH = THIS_FILE_DIR / "README.md"

with open(VERSION_FILE_PATH, "r") as version_file:
    exec(version_file.read())

with open(README_FILE_PATH) as r:
    readme = r.read()

regular_packages = ["boto3", "creevey", "opencv-contrib-python", "pandas", "tqdm"]
dev_packages = ["black", "flake8", "flake8-docstrings", "flake8-import-order"]


setup(
    name="autofocus",
    version=__version__,
    description="Camera traps image classification",
    long_description=readme,
    packages=find_packages(exclude=("tests")),
    install_requires=regular_packages,
    extras_require={"dev": regular_packages + dev_packages},
    author="Greg Gandenberger",
    author_email="gsganden@gmail.com",
    url="https://github.com/UptakeOpenSource/autofocus",
    long_description_content_type="text/markdown",
)
