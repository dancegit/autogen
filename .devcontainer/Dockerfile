# Note: You can use any Debian/Ubuntu based image you want.
FROM mcr.microsoft.com/devcontainers/universal:2

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

# Install Ruby gems
RUN gem install bundler

# Install Go tools
RUN go install golang.org/x/tools/gopls@latest

# Install Groovy
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends groovy

# Install Kotlin
RUN curl -s https://get.sdkman.io | bash \
    && bash -c "source $HOME/.sdkman/bin/sdkman-init.sh && sdk install kotlin"

# Install Scala
RUN curl -s https://get.sdkman.io | bash \
    && bash -c "source $HOME/.sdkman/bin/sdkman-init.sh && sdk install scala"

# Install TypeScript
RUN npm install -g typescript

# Add SDKMAN to PATH
ENV PATH="/root/.sdkman/candidates/kotlin/current/bin:/root/.sdkman/candidates/scala/current/bin:${PATH}"
