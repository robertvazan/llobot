# Standard development environment
#
# Build args:
# - APT_PROXY: Optional apt-get proxy
# - PIP_INDEX_URL: Optional PyPI index URL
# - PIP_TRUSTED_HOST: Optional trusted host for PyPI
# - DEV_USER: Unprivileged user in the container (defaults to rv)

FROM docker.io/library/ubuntu:25.10

# Optional URL of apt-cacher-ng or other proxy server that can cache apt-get downloads.
ARG APT_PROXY=""
RUN if [ -n "$APT_PROXY" ]; then echo "Acquire::http::Proxy \"$APT_PROXY\";" > /etc/apt/apt.conf.d/99proxy; fi

# Install packages.
#
# Project dependencies:
# - python3: Runtime environment
# - python3-pip: Package installer
# - pkg-config: Often required for building python extensions
#
# Convenience tools:
# - bash-completion: Tab completion for bash
# - less: Pager for viewing files
# - locales: To configure LANG and LC_ALL
# - ripgrep: Recursive search CLI
# - sd: Search-and-replace CLI
# - micro: Text editor
# - git: Version control
RUN apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install \
    python3 \
    python3-pip \
    python3-venv \
    sudo \
    pkg-config \
    bash-completion \
    less \
    locales \
    ripgrep \
    sd \
    micro \
    git \
    && apt-get -y clean

# Setup unprivileged user with passwordless sudo.
ARG DEV_USER=rv
RUN (id -u ubuntu >/dev/null 2>&1 && userdel ubuntu || true) && \
    useradd -m -s /bin/bash ${DEV_USER} && \
    usermod -aG sudo ${DEV_USER} && \
    echo '%sudo ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/sudo-nopasswd
USER ${DEV_USER}
WORKDIR /home/${DEV_USER}

# Configure environment
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LESSCHARSET=utf-8 \
    LESS="-R -F -X" \
    TERM=xterm-256color \
    PATH="/home/${DEV_USER}/.local/bin:$PATH"

ENV RIPGREP_CONFIG_PATH=/home/${DEV_USER}/.ripgreprc
RUN echo '--no-require-git' > "$RIPGREP_CONFIG_PATH" && \
    echo 'shopt -s globstar' >> ~/.bashrc && \
    echo 'PS1="(dev) \[\033[01;33m\]\w\[\033[00m\]\\$ "' >> ~/.bashrc

# Configure pip to use cache if provided.
# This affects both the build and subsequent usage of the container.
ARG PIP_INDEX_URL=""
ARG PIP_TRUSTED_HOST=""
RUN if [ -n "$PIP_INDEX_URL" ]; then \
    mkdir -p ~/.config/pip && \
    echo "[global]" > ~/.config/pip/pip.conf && \
    echo "index-url = $PIP_INDEX_URL" >> ~/.config/pip/pip.conf && \
    if [ -n "$PIP_TRUSTED_HOST" ]; then \
        echo "trusted-host = $PIP_TRUSTED_HOST" >> ~/.config/pip/pip.conf; \
    fi; \
    fi

# Install dependencies.
# We use --break-system-packages because we are in a container and we want
# packages to be available globally (or user-globally) without activating venv.
COPY requirements.txt /tmp/requirements.txt
RUN pip install --break-system-packages --user -r /tmp/requirements.txt

CMD ["sleep", "infinity"]
