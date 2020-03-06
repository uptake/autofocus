FROM nvcr.io/nvidia/pytorch:19.10-py3
LABEL maintainer="data-science@shoprunner.com"

# Installing big dependencies early so we don't have to install them
# again every time requirements change
RUN pip install -U pip \
  && pip install fastai==1.0.59 torch==1.3.1 torchtext==0.4.0 torchvision==0.2.1

WORKDIR /autofocus/
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .