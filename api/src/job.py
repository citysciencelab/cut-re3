from enum import Enum
from datetime import datetime
from src.db_handler import DBHandler
import uuid
import json

import config

class JobStatus(Enum):
    """
    Enum for the job status options specified in the WPS 2.0 specification
    """
    accepted = 'accepted'
    running = 'running'
    successful = 'successful'
    failed = 'failed'
    dismissed = 'dismissed'

class Job:
  def __init__(self, job_id=None, process_id=None, parameters={}):
    self.job_id             = job_id
    self.process_id         = process_id
    self.parameters         = parameters
    self.status             = None
    self.message            = None
    self.progress           = None
    self.parameters         = {}
    self.job_start_datetime = None
    self.job_end_datetime   = None

    self.db_handler = DBHandler()

    if job_id is not None:
      self._init_from_db(job_id)
    else:
      self.create()

  def _init_from_db(self, job_id):
    query = """
      SELECT * FROM jobs WHERE job_id = %(job_id)s
    """

    with self.db_handler as db:
      job_details = db.retrieve(query, {'job_id': job_id})

    if len(job_details) > 0:
      data = job_details[0]
      self.process_id =         data['process_id']
      self.status =             data['status']
      self.message =            data['message']
      self.progress =           data['progress']
      self.parameters =         data['parameters']
      self.job_start_datetime = data['job_start_datetime']
      self.job_end_datetime =   data['job_end_datetime']

  def create(self):
    self.job_id     = str(uuid.uuid4())
    self.status     = JobStatus.accepted.value
    self.progress   = 0
    self.message    = ""
    self.job_start_datetime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    self.job_end_datetime   = None
    self.save()

  def save(self):
    query = """
      INSERT INTO jobs
      (job_id, process_id, status, progress, parameters, message, job_start_datetime, job_end_datetime)
      VALUES
      (%(job_id)s, %(process_id)s, %(status)s, %(progress)s, %(parameters)s, %(message)s, %(job_start_datetime)s, %(job_end_datetime)s)
    """

    data = {
      "job_id":             self.job_id,
      "process_id":         self.process_id,
      "status":             self.status,
      "progress":           self.progress,
      "parameters":         json.dumps(self.parameters),
      "message":            self.message,
      "job_start_datetime": self.job_start_datetime,
      "job_end_datetime":   self.job_end_datetime
    }

    with self.db_handler as db:
      db.insert(query, data)

  def details(self):
    job_start_datetime = None
    job_end_datetime = None

    if self.job_start_datetime:
      job_start_datetime = self.job_start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    if self.job_end_datetime:
      job_end_datetime = self.job_end_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    job_details = {
      'processID':          self.process_id,
      'jobID':              self.job_id,
      'status':             self.status,
      'message':            self.message,
      'progress':           self.progress,
      'parameters':         self.parameters,
      'job_start_datetime': job_start_datetime,
      'job_end_datetime':   job_end_datetime
    }

    if self.status in (
      JobStatus.successful, JobStatus.running, JobStatus.accepted):
        # TODO
        job_result_url = f"{config.server_url}/jobs/{self.job_id}/results.geojson"  # noqa

        job_details['links'] = [{
            'href': job_result_url,
            'rel': 'about',
            'type': 'application/json',
            'title': f'results of job {self.job_id} as JSON'
        }]
    return job_details

  def delete():
    raise Exception(f'******* Deleting job not implemented!')

  def __str__(self):
    return f"""
      ----- src.job.Job -----
      job_id={self.job_id}, process_id={self.process_id},
      status={self.status}, message={self.message},
      progress={self.progress}, parameters={self.parameters},
      job_start_datetime={self.job_start_datetime},
      job_end_datetime={self.job_end_datetime}
    """

  def __repr__(self):
    return f'src.job.Job(job_id={self.job_id})'

# TODO: this is only mocked
def all_jobs_as_json():
  with open("example_api_jobs.json") as f:
    result = f.read()
  return result
