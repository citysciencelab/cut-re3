from flask import Flask
import logging
from routes.processes import processes

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(processes, url_prefix='/processes')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5001, debug=True)
