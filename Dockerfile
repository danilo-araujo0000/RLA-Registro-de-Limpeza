# Use Ubuntu como base
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Sao_Paulo

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3.11-dev \
    wget \
    unzip \
    libaio1 \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Oracle Instant Client (ainda necessário para queries diretas via oracledb)
RUN mkdir -p /opt/oracle && \
    cd /opt/oracle && \
    wget https://download.oracle.com/otn_software/linux/instantclient/2350000/instantclient-basic-linux.x64-23.5.0.24.07.zip && \
    unzip instantclient-basic-linux.x64-23.5.0.24.07.zip && \
    rm instantclient-basic-linux.x64-23.5.0.24.07.zip && \
    echo /opt/oracle/instantclient_23_5 > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_23_5:$LD_LIBRARY_PATH
ENV PATH=/opt/oracle/instantclient_23_5:$PATH

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles

EXPOSE 8000

CMD python3 manage.py collectstatic --noinput && \
    python3 manage.py migrate && \
    python3 manage.py migrate --database=oracle || true && \
    python3 create_superuser.py && \
    gunicorn --bind 0.0.0.0:8000 --workers 3 higiene_project.wsgi:application
