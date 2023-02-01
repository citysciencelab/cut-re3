from flask import Flask, Blueprint, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

import logging
import json
import os
from routes.processes import processes
from routes.jobs import jobs
from src.errors import CustomException

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins = os.environ.get("CORS_URL_REGEX", "*"))

api = Blueprint('api', __name__, url_prefix='/api')
api.register_blueprint(processes, url_prefix='/processes')
api.register_blueprint(jobs, url_prefix='/jobs')

app.register_blueprint(api)

@app.errorhandler(CustomException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.errorhandler(HTTPException)
def handle_http_exception(error):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = error.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": error.code,
        "name": error.name,
        "description": error.description,
    })
    response.content_type = "application/json"
    return response

if __name__ == '__main__':
  # TODO: DO NOT RUN flask with DEBUG in production!!
  # Use a production WSGI server instead.
  app.run(host='0.0.0.0', port=5001, debug=True)


# gunicorn -w 4 -b :8080 main:app --timeout 3600
# -w number of processes to run
# should be CPU * 2
# default: 1
