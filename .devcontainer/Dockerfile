FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y \
        pypy3 \
        python3.8-full \
        python3.9-full \
        python3.10-full \
        python3.11-full \
        tox && \
    rm -rf /var/lib/apt/lists/*