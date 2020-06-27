FROM ubuntu:18.04

ARG db_host
ARG db_user
ARG db_password
ARG db_schema=simplewiki
ARG proj=demo_data_pipeline

WORKDIR /home/root

RUN mkdir ./$proj \
    && mkdir ./$proj/logs \
    && mkdir ./$proj/dump \
    && echo "db: $db_schema" >> ./$proj/db_details.yaml \
    && echo "host: $db_host" >> ./$proj/db_details.yaml \
    && echo "user: $db_user" >> ./$proj/db_details.yaml \
    && echo "pw: $db_password" >> ./$proj/db_details.yaml

COPY api.py \
    db_controller.py \
    db_setup_refresh.py \
    requirements.txt \
    ./$proj/

RUN apt-get update && apt-get install -y \
    python3-pip \
    mysql-client-core-5.7

RUN pip3 install -r ./$proj/requirements.txt

EXPOSE 5000
