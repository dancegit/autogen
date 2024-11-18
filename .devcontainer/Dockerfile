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

# Install Ruby 3.0 using rbenv
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    git \
    libssl-dev \
    libreadline-dev \
    zlib1g-dev \
    autoconf \
    bison \
    build-essential \
    libyaml-dev \
    libreadline-dev \
    libncurses5-dev \
    libffi-dev \
    libgdbm-dev

RUN git clone https://github.com/rbenv/rbenv.git ~/.rbenv \
    && echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.bashrc \
    && echo 'eval "$(rbenv init -)"' >> ~/.bashrc \
    && git clone https://github.com/rbenv/ruby-build.git ~/.rbenv/plugins/ruby-build

ENV PATH=/root/.rbenv/bin:$PATH
RUN /bin/bash -c "source ~/.bashrc && rbenv init - && rbenv install 3.0.0 && rbenv global 3.0.0"

RUN echo 'gem: --no-document' > ~/.gemrc
RUN /bin/bash -c "source ~/.bashrc && gem install bundler"

# Verify Ruby version and Bundler installation
RUN /bin/bash -c "source ~/.bashrc && ruby --version && bundler --version"

# Install Go
RUN wget https://golang.org/dl/go1.21.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz && \
    rm go1.21.5.linux-amd64.tar.gz

# Set Go environment variables
ENV GOROOT=/usr/local/go
ENV PATH=$PATH:/usr/local/go/bin
ENV GOPATH=/root/go
ENV PATH=$PATH:$GOPATH/bin

# Install Go tools
RUN /usr/local/go/bin/go install golang.org/x/tools/gopls@latest

# Install Groovy
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends groovy

# Install SDKMAN
RUN curl -s "https://get.sdkman.io" | bash

# Set up SDKMAN environment variables
ENV SDKMAN_DIR="/root/.sdkman"
ENV PATH="${SDKMAN_DIR}/bin:${PATH}"

# Source SDKMAN and install Kotlin and Scala
RUN bash -c "source ${SDKMAN_DIR}/bin/sdkman-init.sh && \
    sdk install kotlin && \
    sdk install scala"

# Install TypeScript
RUN npm install -g typescript

# Add SDKMAN-installed binaries to PATH
ENV PATH="${SDKMAN_DIR}/candidates/kotlin/current/bin:${SDKMAN_DIR}/candidates/scala/current/bin:${PATH}"

# Source SDKMAN in .bashrc for interactive shells
RUN echo 'source "${SDKMAN_DIR}/bin/sdkman-init.sh"' >> /root/.bashrc

# Set SHELL to bash and use login shell to ensure .bashrc is sourced
SHELL ["/bin/bash", "-l", "-c"]
