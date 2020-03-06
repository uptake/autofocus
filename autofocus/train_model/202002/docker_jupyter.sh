nvidia-docker run \
  -e NVIDIA_VISIBILE_DEVICES=all \
  --ipc=host \
  -v "${PWD}:/autofocus" \
  -v $IMAGE_DIR:/images/ \
  -p 8888:8888 \
  autofocus_train:202002 \
  jupyter lab --allow-root --ip 0.0.0.0 --no-browser --NotebookApp.token='' --NotebookApp.password=''
