FROM nvidia/cuda:11.2.2-cudnn8-runtime-ubuntu20.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON_VERSION=3.10.11

# Install system dependencies for Python build
RUN apt-get update && apt-get install -y \
    wget build-essential \
    libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev \
    curl llvm libncursesw5-dev \
    xz-utils tk-dev libxml2-dev \
    libxmlsec1-dev libffi-dev \
    liblzma-dev libgl1 libglib2.0-0 git

# Install Python 3.10.11 from source
RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar -xvf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall && \
    cd .. && rm -rf Python-${PYTHON_VERSION}*

# Set Python 3.10.11 as default
RUN ln -s /usr/local/bin/python3.10 /usr/bin/python && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python && \
    ln -s /usr/local/bin/pip3 /usr/bin/pip

# Install Poetry
RUN pip install poetry
RUN pip install python-multipart
# Set working directory
WORKDIR /app

# Copy project files from backend_microservice
COPY pyproject.toml poetry.lock* README.md /app/
COPY src /app/src
COPY models /models
COPY config.json /app/config.json

# 🔹 Copy shared code from sibling directory
COPY src/cv2_group /app/cv2_group

# Install dependencies with Poetry (no venvs)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Run the app
CMD ["poetry", "run", "uvicorn", "backend_microservice.app:app", "--host", "0.0.0.0", "--port", "8000"]
