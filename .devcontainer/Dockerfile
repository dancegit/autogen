# Use the official Debian-based Python image
FROM python:3.9-slim-buster

# Install additional OS packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    python3-pip \
    nodejs \
    npm \
    default-jdk \
    golang \
    ruby \
    ruby-dev \
    libssl-dev \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install any global npm packages
RUN npm install -g yarn

# Install any global pip packages
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir \
    pylint \
    black \
    mypy

# Install Ruby using apt
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    ruby-full \
    ruby-bundler

# Set Ruby version and install bundler
RUN ruby --version && gem install bundler

# Install Go tools
RUN go install golang.org/x/tools/gopls@latest

# Install Groovy
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends groovy

# Install SDKMAN
RUN curl -s "https://get.sdkman.io" | bash

# Install Kotlin and Scala
RUN bash -c "source /root/.sdkman/bin/sdkman-init.sh && \
    sdk install kotlin && \
    sdk install scala"

# Install TypeScript
RUN npm install -g typescript

# Add SDKMAN to PATH
ENV PATH="/root/.sdkman/candidates/kotlin/current/bin:/root/.sdkman/candidates/scala/current/bin:${PATH}"

# Source SDKMAN in .bashrc
RUN echo "source /root/.sdkman/bin/sdkman-init.sh" >> /root/.bashrc
