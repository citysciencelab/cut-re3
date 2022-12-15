from flask import Flask, Blueprint

import logging
from routes.processes import processes

logger = logging.getLogger(__name__)

app = Flask(__name__)

api = Blueprint('api', __name__, url_prefix='/api')
api.register_blueprint(processes, url_prefix='/processes')

app.register_blueprint(api)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5001, debug=True)
