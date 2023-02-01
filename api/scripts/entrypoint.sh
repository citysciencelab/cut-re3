#!/bin/bash
set -e

if [ $FLASK_DEBUG == 1 ]
then
  echo "Running API Server in debug mode."
  python main.py
else
  echo "Running API Server in production mode."
  gunicorn --workers=4 --bind=0.0.0.0:5001 main:app
fi
