from flask import Response, Blueprint, request
from src.process import all_processes_as_json
from src.process import Process
import json

processes = Blueprint('processes', __name__)

@processes.route('/', defaults={'page': 'index'})
def index(page):
  result = all_processes_as_json()
  return Response(result, mimetype='application/json')

@processes.route('/<path:process_id>', methods = ['GET'])
def show(process_id=None):
  process = Process(process_id)
  return Response(process.to_json(), mimetype='application/json')

@processes.route('/<path:process_id>/execution', methods = ['POST'])
def execute(process_id=None):
  process = Process(process_id)
  result = process.execute(request.json["inputs"])
  return Response(json.dumps(result), status=201, mimetype='application/json')

# TODO: proper error handling
@processes.errorhandler(404)
def page_not_found(e):
    return Response(json.dumps({"error": e}), mimetype='application/json')
