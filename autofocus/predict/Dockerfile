FROM continuumio/miniconda3
LABEL maintainer="data-science@shoprunner.com"
USER root

RUN apt-get update -qq \
  && apt-get install --no-install-recommends -y gunicorn \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN conda install pytorch=1.0.1 torchvision -c pytorch \
  && conda install -c fastai fastai=1.0.50.post1 \
  && conda clean -y --all

COPY . /image_api
WORKDIR /image_api

RUN python -m pip install -r requirements.txt

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.app:app" ]
