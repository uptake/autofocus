# Autofocus Training 2020/02

## Prerequisites

- Create an AWS account, install the AWS CLI tool (`pip install awscli`), and set up your AWS config and credentials (`aws configure`).
- Install `nvidia-docker` for running with a GPU (highly recommended).

## Get the Data

Follow the instructions in [the repo README](../../../README.md) for downloading the data for 2012-2014, 2016, and 2017.

## Build Docker Container

```bash
docker build . -t autofocus_train:202002
```

## Process the Data

```bash
./docker_bash.sh
python prepare_data.py
```

## Start Jupyter Server Inside Docker Container

With a GPU:

```bash
./docker_jupyter.sh
```

Without a GPU:

```bash
./docker_jupyter_cpu.sh
```

Then open a browser to `<host>:8888/lab`.
