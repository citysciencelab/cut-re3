from flask import Response, Blueprint, request
from src.processes import all_processes
from src.process import Process
import json

processes = Blueprint('processes', __name__)

@processes.route('/', defaults={'page': 'index'})
def index(page):
  result = all_processes()
  return Response(json.dumps(result), mimetype='application/json')

@processes.route('/<path:process_id>', methods = ['GET'])
def show(process_id=None):
  process = Process(process_id)
  return Response(process.to_json(), mimetype='application/json')

@processes.route('/<path:process_id>/execution', methods = ['POST'])
def execute(process_id=None):
  process = Process(process_id)
  result = process.execute(request.json)
  return Response(json.dumps(result), status=201, mimetype='application/json')
