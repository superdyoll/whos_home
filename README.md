# whos_home

A series of scripts to automate checking who is home

# Installation

Install the required packages:
```bash
# Global packages
sudo apt-get install nmap
sudo pip install virtualenv

# Python packages
virtualenv venv
source venv/bin/activate
pip install Flask pytz
```

set up a CRON job to run `sudo ./whos_home.sh | python parse_whos_home_output.py` every 5 minutes or so.

start the flask server with `export FLASK_APP=webserver.py; python -m flask run`
