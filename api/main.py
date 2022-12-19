from flask import Flask, Blueprint

import logging
from routes.processes import processes
from routes.jobs import jobs

logger = logging.getLogger(__name__)

app = Flask(__name__)

api = Blueprint('api', __name__, url_prefix='/api')
api.register_blueprint(processes, url_prefix='/processes')
api.register_blueprint(jobs, url_prefix='/jobs')

app.register_blueprint(api)

if __name__ == '__main__':
  # TODO: DO NOT RUN flask with DEBUG in production!!
  # Use a production WSGI server instead.
  app.run(host='0.0.0.0', port=5001, debug=True)
