#!/bin/bash
set -e

if [ $FLASK_DEBUG == 1 ]
then
  echo "Running API Server in debug mode."
  python main.py
else
  echo "Running API Server in production mode."
  NUMBER_OF_WORKERS="${NUMBER_OF_WORKERS:-2}"
  echo "Running gunicorn with ${NUMBER_OF_WORKERS} workers."
  gunicorn --workers=$NUMBER_OF_WORKERS --bind=0.0.0.0:5001 main:app
fi
