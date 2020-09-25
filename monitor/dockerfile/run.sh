#!/bin/bash
cd /usr
export FLASK_APP=app.py
flask run -h 0.0.0.0 -p 5000
