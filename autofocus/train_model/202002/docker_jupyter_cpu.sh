docker run \
  --ipc=host \
  -v "${PWD}:/autofocus" \
  -v /home/ec2-user/.aws/:/root/.aws/ \
  -v $AUTOFOCUS_DATA_DIR:/autofocus/data/ \
  -e AUTOFOCUS_DATA_DIR=/autofocus/data/ \
  -p 8888:8888 \
  autofocus_train:202002 \
  jupyter lab --allow-root --ip 0.0.0.0 --no-browser --NotebookApp.token='' --NotebookApp.password=''
