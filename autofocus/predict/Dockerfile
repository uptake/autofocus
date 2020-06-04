FROM continuumio/miniconda3
MAINTAINER data-science@shoprunner.com
USER root

RUN apt-get update -qq \
  && apt-get install --no-install-recommends -y gunicorn \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN conda install pytorch=1.3.1 torchvision -c pytorch \
  && conda install -c fastai fastai=1.0.59 \
  && conda clean -y --all

COPY requirements.txt /image_api/requirements.txt
RUN python -m pip install -r /image_api/requirements.txt

COPY . /image_api
WORKDIR /image_api

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.app:app" ]
