# This image fills the gap of needing ruby, docker, and helm in a single Cloud Builder step 
# (since we have ruby scripts that call out to these other tools).

FROM ubuntu:16.04

ENV KUBECTL_VERSION="v1.11.2"
ENV HELM_VERSION="v2.10.0"
ENV TERRAFORM_VERSION="0.11.14"
ENV PATH="/builder/google-cloud-sdk/bin:${PATH}"

# These env variables are needed to prevent Click from complaining
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get -y update \
    # Install base dependencies (including Make)
    && apt-get -y install \
        apt-transport-https \
        software-properties-common \
        ca-certificates \
        curl \
        wget \
        build-essential \
        python2.7 \
        python3 \
        python3-pip \
        python-dev \
        python-setuptools \
        python-software-properties \
        unzip \
    # Setup docker PPA
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - \
    && apt-key fingerprint 0EBFCD88 \
    && add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu xenial edge" \ 
    # Setup git PPA
    && add-apt-repository ppa:git-core/ppa \
    # Install build tools
    && apt-get -y update \
    && apt-get -y install \
        docker-ce \
        ruby \
        git \
    # Setup Google Cloud SDK (latest)
    && mkdir -p /builder \
    && wget -qO- https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz | tar zxv -C /builder \
    && CLOUDSDK_PYTHON="python2.7" /builder/google-cloud-sdk/install.sh --usage-reporting=false --bash-completion=false --disable-installation-options \
    # Install crcmod: https://cloud.google.com/storage/docs/gsutil/addlhelp/CRC32CandInstallingcrcmod
    && easy_install -U pip==20.3.4 \
    && pip install -U crcmod \
    # Install kubectl
    && gcloud -q components install kubectl \
    # Install Helm
    && wget -q https://storage.googleapis.com/kubernetes-helm/helm-${HELM_VERSION}-linux-amd64.tar.gz -O - | tar -xzO linux-amd64/helm > /usr/local/bin/helm \
    && chmod +x /usr/local/bin/helm \
    # Install Terraform
    && wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    # Clean up
    && apt-get -y remove gcc python-dev python-setuptools wget \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf ~/.config/gcloud \
    # Make the kubails folder
    && mkdir -p /kubails/kubails

COPY ./kubails /kubails/kubails
COPY ./setup.py /kubails/
RUN pip3 install /kubails
