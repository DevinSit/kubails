FROM postgres:11.1

ENV PATH="/builder/google-cloud-sdk/bin:${PATH}"

RUN apt-get -y update \
    # Install base dependencies
    && apt-get -y install \
        apt-transport-https \
        software-properties-common \
        ca-certificates \
        curl \
        wget \
        build-essential \
        python2.7 \
        python-dev \
        python-setuptools \
    # Setup Google Cloud SDK (latest)
    && mkdir -p /builder \
    && wget -qO- https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz | tar zxv -C /builder \
    && CLOUDSDK_PYTHON="python2.7" /builder/google-cloud-sdk/install.sh --usage-reporting=false --bash-completion=false --disable-installation-options \
    # Install crcmod: https://cloud.google.com/storage/docs/gsutil/addlhelp/CRC32CandInstallingcrcmod
    && easy_install -U pip \
    && pip install -U crcmod \
    # Install kubectl
    && gcloud -q components install kubectl \
    # Clean up
    && apt-get -y remove gcc python-dev python-setuptools wget \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf ~/.config/gcloud

COPY backup_database.sh .

CMD ["sh", "./backup_database.sh"]
