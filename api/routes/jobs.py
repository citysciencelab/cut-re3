from flask import Response, Blueprint, request
from src.job import Job
from src.jobs import get_jobs
import json

jobs = Blueprint('jobs', __name__)

@jobs.route('/', defaults={'page': 'index'})
def index(page):
  # OGC API standard: support the following parameters:
  # https://docs.ogc.org/is/18-062r2/18-062r2.html#rc_job-list
  # still missing: minDuration, maxDuration, datetime
  args = request.json if request.is_json else {}
  result = get_jobs(args)
  return Response(json.dumps(result), mimetype='application/json')

@jobs.route('/<path:job_id>/results', methods = ['GET'])
def results(job_id=None):
  with open("data/results_XS.geojson") as f:
      results = f.read()
  return Response(results, mimetype='application/json')

@jobs.route('/<path:job_id>', methods = ['GET'])
def show(job_id=None):
  job = Job(job_id)

  if job.errors:
    result = {"errors": job.errors}
  else:
    result = job.display()

  return Response(json.dumps(result), mimetype='application/json')

@jobs.route('/<path:job_id>', methods = ['DELETE'])
def delete(job_id=None):
  job = Job(job_id)
  job.delete()
  result = {"error": "not implemented"}
  return Response(json.dumps(result), mimetype='application/json')

@jobs.errorhandler(404)
def page_not_found(e):
  result = {
    "type": type(e),
    "title": str(e),
    "status": 0,
    "detail": str(e),
    "instance": ""
  }
  return Response(json.dump(result), mimetype='application/json')
