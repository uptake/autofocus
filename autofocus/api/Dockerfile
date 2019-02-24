
FROM debian:stretch
MAINTAINER Dan Acheson <Daniel.Acheson@uptake.com>

# install debian packages
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -qq \
 && apt-get install --no-install-recommends -y \
    # install essentials
    build-essential \
    g++ \
    git \
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-virtualenv \
    python3-wheel \
    pkg-config \
    # requirements for numpy
    libopenblas-base \
    gunicorn \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt ./requirements.txt
ADD image_classify ./image_classify
#ADD app ./app
COPY ./app/* ./
RUN pip3 install ./image_classify
RUN pip3 install -r requirements.txt

#WORKDIR /app



EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080","wsgi:app" ]