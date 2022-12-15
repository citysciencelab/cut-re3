from flask import Blueprint
from src.processes import list_all

processes = Blueprint('processes', __name__)

@processes.route('/', defaults={'page': 'index'})
@processes.route('/<page>')
def list_processes(page):
  return list_all()
