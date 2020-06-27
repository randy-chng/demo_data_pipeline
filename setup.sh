#!/bin/bash

readonly PROJ=demo_data_pipeline

sudo timedatectl set-timezone Asia/Singapore

echo

echo Welcome to the setup of $PROJ

echo

read -p 'Provide MySQL IP Address: ' host

read -p 'Provide MySQL User: ' user

read -p 'Provide MySQL Password: ' password

echo

cat <<EOM >~/$PROJ/db_details.yaml
db: simplewiki
host: $host
user: $user
pw: $password
EOM

echo Installing os dependencies

sudo apt-get update

sudo apt-get install python3-pip mysql-client-core-5.7 -y

echo

echo Creating python virtual environment

sudo pip3 install virtualenv

cd ~/ && virtualenv -p python3 venv

source ~/venv/bin/activate

echo

echo Installing python dependencies

pip3 install -r ~/$PROJ/requirements.txt

echo

echo Creating default directories

mkdir ~/$PROJ/logs

mkdir ~/$PROJ/dump
