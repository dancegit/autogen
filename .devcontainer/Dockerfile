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
RUN wget https://golang.org/dl/go1.17.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.17.linux-amd64.tar.gz && \
    rm go1.17.linux-amd64.tar.gz

# Set Go environment variables
ENV GOROOT=/usr/local/go
ENV PATH=$PATH:/usr/local/go/bin

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
ENV PATH=/root/.sdkman/candidates/kotlin/current/bin:/root/.sdkman/candidates/scala/current/bin:${PATH}

# Source SDKMAN in .bashrc
RUN echo "source /root/.sdkman/bin/sdkman-init.sh" >> /root/.bashrc
