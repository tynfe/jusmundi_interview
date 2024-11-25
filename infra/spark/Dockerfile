FROM openjdk:11.0.11-jre-slim-buster as builder

# Add Dependencies for PySpark
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    xz-utils \
    vim \
    software-properties-common \
    ssh \
    net-tools \
    ca-certificates \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libsqlite3-dev \
    libreadline-dev \
    libffi-dev \
    libbz2-dev \
    liblzma-dev \
    git

#RUN apt-get update && apt-get install -y wget xz-utils build-essential

RUN wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tar.xz && \
    tar -xf Python-3.12.0.tar.xz && \
    cd Python-3.12.0 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall
#    cd .. && \
#    rm -rf Python-3.12.0 Python-3.12.0.tar.xz

RUN update-alternatives --install "/usr/bin/python" "python" "/usr/local/bin/python3.12" 1

RUN pip3.12 install poetry

ENV SPARK_VERSION=3.5.3 \
HADOOP_VERSION=3 \
SPARK_HOME=/opt/spark \
PYTHONHASHSEED=1

RUN wget --no-verbose -O apache-spark.tgz "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
&& mkdir -p /opt/spark \
&& tar -xf apache-spark.tgz -C /opt/spark --strip-components=1 \
&& rm apache-spark.tgz


FROM builder as apache-spark

WORKDIR /opt/spark

ENV SPARK_MASTER_PORT=7077 \
SPARK_MASTER_WEBUI_PORT=8080 \
SPARK_LOG_DIR=/opt/spark/logs \
SPARK_MASTER_LOG=/opt/spark/logs/spark-master.out \
SPARK_WORKER_LOG=/opt/spark/logs/spark-worker.out \
SPARK_WORKER_WEBUI_PORT=8080 \
SPARK_WORKER_PORT=7000 \
SPARK_MASTER="spark://commons:7077"

EXPOSE 8080 7077 7000

RUN mkdir -p $SPARK_LOG_DIR && \
touch $SPARK_MASTER_LOG && \
touch $SPARK_WORKER_LOG && \
ln -sf /dev/stdout $SPARK_MASTER_LOG && \
ln -sf /dev/stdout $SPARK_WORKER_LOG

COPY start-spark.sh /


CMD ["/bin/bash", "/start-spark.sh"]