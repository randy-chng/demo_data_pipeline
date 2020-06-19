# Server Setup on GCP

## Step 1
Spin up Cloud SQL instance (MySQL 5.7)

** Take note of Cloud SQL instance ip address, user and password to update details in project

## Step 2
Spin up GCE instance (Ubuntu 18.04).

** Take note of GCE instance ip address and add into Cloud SQL instance's Authorized networks

## Step 3
SSH into instance and clone the project.
```
cd ~/ && git clone https://github.com/randy-chng/demo_web_api_data_pipeline.git
```

Once clone is done, run the following commands to
- provide MySQL details [ip address | user | password]
- auto install requirements
```
chmod +x ~/demo_web_api_data_pipeline/setup.sh
cd ~/demo_web_api_data_pipeline && ./setup.sh
```

## Step 4
Run following commands to run data pipeline service
```
source ~/venv/bin/activate
cd ~/demo_web_api_data_pipeline && python3 db_setup_refresh.py
```

Run following commands to run api service
```
source ~/venv/bin/activate
cd ~/demo_web_api_data_pipeline && nohup python3 api.py &
```

To interact with the api, browsers like Chrome or curl or python can be used.

** Replace 34.87.87.72 with your server address when hosting this project on your own

For browser, visit either links
- http://34.87.87.72:5000/api/v1/resources/outdated?category=American_people_stubs
- http://34.87.87.72:5000/api/v1/resources/query?sql=select%20*%20from%20category%20limit%203

For curl
```
curl http://34.87.87.72:5000/api/v1/resources/outdated?category=American_people_stubs
curl http://34.87.87.72:5000/api/v1/resources/query?sql=select%20*%20from%20category%20limit%203
```

For python, refer to example_call_api.py

## Step 5 (Optional)
For a monthly refresh of simplewiki data, configure cron by running the following commands.
Schedule will be every 1st day of the month at 12am.
```
chmod +x ~/demo_web_api_data_pipeline/refresh_data.sh
(crontab -l; echo "0 0 1 * * $HOME/demo_web_api_data_pipeline/refresh_data.sh") | crontab -
```