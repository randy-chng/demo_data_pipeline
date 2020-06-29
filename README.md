## Overview

This project demonstrates
- a batch processing data pipeline with
- an API service to query ingested data

#### Data pipeline details (db_setup_refresh.py)
- Download compressed MySQL dumps
    - Dump, https://dumps.wikimedia.org/simplewiki/latest/
    - Metadata, https://meta.wikimedia.org/wiki/Data_dumps/What%27s_available_for_download#Database_tables
- Uncompress downloaded MySQL dumps
- Create schema (simplewiki) in MySQL
- Load uncompressed MySQL dumps into simplewiki
- Preprocess data and store results to support 2nd API endpoint

#### API service details (api.py)
- Exposes 2 endpoints
- 1st endpoint takes in a SQL select query, executes query on simplewiki and returns the result
- 2nd endpoint takes in a top 10 category name and returns the most outdated page associated to the category

#### Resulting tables in simplewiki
- From MySQL dumps
    - categorylinks
    - category
    - page
    - pagelinks
- From preprocessing data
    - outdated_pages_in_top_category (intermediate results)
    - most_outdated_page_in_top_category (final results)

## Installation

### Database
Spin up Cloud SQL instance (MySQL 5.7)

** Note Cloud SQL instance ip address, user and password for application set up

### Application (Docker)

#### Step 1
Spin up GCE instance (Container Optimized OS)

** Note GCE instance ip address and add into Cloud SQL instance's Authorized networks

#### Step 2
SSH into instance and clone project
```
cd ~/ && git clone https://github.com/randy-chng/demo_data_pipeline.git
```

#### Step 3
Build image and provide MySQL details
```
cd ~/demo_data_pipeline
docker image build --tag demo --build-arg db_host=[ip address] --build-arg db_user=[user] --build-arg db_password=[password] --file Dockerfile .
```

#### Step 4
Run created image
```
docker run --name test --publish 5000:5000 -di [image id]
```

#### Step 5
Access created container
```
docker exec -it [container id] /bin/bash
```

#### Step 6
Run following commands to activate data pipeline service
```
python3 db_setup_refresh.py
```

Run following commands to activate api service
```
nohup python3 api.py &
```

### Application (Non-Docker)

#### Step 1
Spin up GCE instance (Ubuntu 18.04)

** Take note of GCE instance ip address and add into Cloud SQL instance's Authorized networks

#### Step 2
SSH into instance and clone project
```
cd ~/ && git clone https://github.com/randy-chng/demo_data_pipeline.git
```

#### Step 3
Run following commands to
- provide MySQL details [ip address | user | password]
- auto install requirements
```
chmod +x ~/demo_data_pipeline/setup.sh
cd ~/demo_data_pipeline && ./setup.sh
```

#### Step 4
Run following commands to activate data pipeline service
```
source ~/venv/bin/activate
cd ~/demo_data_pipeline && python3 db_setup_refresh.py
```

Run following commands to activate api service
```
source ~/venv/bin/activate
cd ~/demo_data_pipeline && nohup python3 api.py &
```

## API Interaction

To interact with api, browsers (Chrome, etc.) or python or curl can be used

** Replace 34.87.87.72 with appropriate address

For browser, visit either links
- http://34.87.87.72:5000/api/v1/resources/outdated?category=American_people_stubs
- http://34.87.87.72:5000/api/v1/resources/query?sql=select%20*%20from%20category%20limit%203

For python, refer to example_call_api.ipynb

For curl
```
curl http://34.87.87.72:5000/api/v1/resources/outdated?category=American_people_stubs
curl http://34.87.87.72:5000/api/v1/resources/query?sql=select%20*%20from%20category%20limit%203
```

## Scheduling Data Pipeline Service (Optional)
For a monthly refresh of simplewiki data, configure cron by running following commands.
Schedule will be every 1st day of the month at 12am.
```
chmod +x ~/demo_data_pipeline/refresh_data.sh
(crontab -l; echo "0 0 1 * * $HOME/demo_data_pipeline/refresh_data.sh") | crontab -
```