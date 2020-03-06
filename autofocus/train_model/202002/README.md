# Autofocus Training 2020/02

## Install nvidia-docker

The docker commands provided all use nvidia-docker, which is recommended for running with a GPU.

## Build Docker Container

```
docker build . -t autofocus_train:202002
```

## Start Jupyter Server Inside Docker Container

```bash
sh docker_jupyter.sh
```

Then open a browser to `<host>:8888/lab`.
