from flask import Blueprint
from src.jobs import Job, all_jobs_as_json
from flask import Response
import json

jobs = Blueprint('jobs', __name__)

@jobs.route('/', defaults={'page': 'index'})
def index(page):
  result = all_jobs_as_json()
  return Response(result, mimetype='application/json')

@jobs.route('/<path:job_id>')
def show(job_id=None):
  job = Job(job_id)
  return Response(json.dumps(job.details()), mimetype='application/json')

@jobs.errorhandler(404)
def page_not_found(e):
    return Response(json.dump({"error": e}), mimetype='application/json')
