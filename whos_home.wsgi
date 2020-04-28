#!/usr/bin/env python3
import sys
# Activate venv
activate_this = '/home/www/whos_home/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
# set the path to here.
sys.path.insert(0,'/home/www/whos_home')
# import the webserver
from webserver import app as application
