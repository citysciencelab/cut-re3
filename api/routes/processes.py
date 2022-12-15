from flask import Blueprint
from src.processes import all_processes_as_json
from flask import Response

processes = Blueprint('processes', __name__)

@processes.route('/', defaults={'page': 'index'})
@processes.route('/<page>')
def list_processes(page):
  result = all_processes_as_json()
  return Response(result, mimetype='application/json')
