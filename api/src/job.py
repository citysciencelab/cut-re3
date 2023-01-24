from datetime import datetime
import uuid
import json
import configs.config as config
import base64
from src.db_handler import DBHandler
from src.job_status import JobStatus
import requests
import logging
import yaml

PROVIDERS = yaml.safe_load(open('./configs/providers.yml'))

class Job:
  DISPLAYED_ATTRIBUTES = [
      "processID", "type", "jobID", "status", "message",
      "created", "started", "finished", "updated", "progress",
      "links", "parameters"
    ]

  SORTABLE_COLUMNS = ['created', 'finished', 'updated', 'started', 'process_id', 'status', 'message']

  def __init__(self, job_id=None, process_id_base64=None, parameters={}):
    self.job_id = job_id
    self.process_id        = None
    self.provider_prefix   = None
    self.provider_url      = None
    self.process_id_base64 = process_id_base64
    self.parameters        = parameters
    self.status            = None
    self.message           = None
    self.progress          = None
    self.parameters        = parameters
    self.created           = None
    self.started           = None
    self.finished          = None
    self.updated           = None

    if process_id_base64:
      data = json.loads(base64.urlsafe_b64decode(process_id_base64.encode()).decode())
      self.process_id      = data['process_id']
      self.provider_prefix = data['provider_prefix']
      self.provider_url    = PROVIDERS[self.provider_prefix]['url']

    if not self._init_from_db(job_id):
      self._create()

  def _init_from_db(self, job_id):
    query = """
      SELECT * FROM jobs WHERE job_id = %(job_id)s
    """
    with DBHandler() as db:
      job_details = db.run_query(query, query_params={'job_id': job_id})

    if len(job_details) > 0:
      self._init_from_dict(dict(job_details[0]))
      return True
    else:
      return False

  def _init_from_dict(self, data):
    self.job_id          = data['job_id']
    self.process_id      = data['process_id']
    self.provider_prefix = data['provider_prefix']
    self.provider_url    = data['provider_url']
    self.status          = data['status']
    self.message         = data['message']
    self.created         = data['created']
    self.started         = data['started']
    self.finished        = data['finished']
    self.updated         = data['updated']
    self.progress        = data['progress']
    self.parameters      = data['parameters']

  def _create(self):
    self.job_id    = self.job_id if self.job_id else str(uuid.uuid4())
    self.status    = JobStatus.accepted.value
    self.progress  = 0
    self.message   = ""
    self.created   = datetime.utcnow()
    self.started   = None
    self.updated   = datetime.utcnow()
    self.finished  = None

    query = """
      INSERT INTO jobs
      (job_id, process_id, provider_prefix, provider_url, status, progress, parameters, message, created, started, finished, updated)
      VALUES
      (%(job_id)s, %(process_id)s, %(provider_prefix)s, %(provider_url)s, %(status)s, %(progress)s, %(parameters)s, %(message)s, %(created)s, %(started)s, %(finished)s, %(updated)s)
    """
    with DBHandler() as db:
      db.run_query(query, query_params=self._to_dict())

    logging.info(f" --> Job {self.job_id} for {self.process_id} created.")

  def _to_dict(self):
    return {
      "process_id": self.process_id,
      "job_id":     self.job_id,
      "provider_prefix": self.provider_prefix,
      "provider_url": self.provider_url,
      "status":     self.status,
      "message":    self.message,
      "created":    self.created,
      "started":    self.started,
      "finished":   self.finished,
      "updated":    self.updated,
      "progress":   self.progress,
      "parameters": json.dumps(self.parameters)
    }

  def save(self):
    self.updated = datetime.utcnow()
    query = """
      UPDATE jobs SET
      (process_id, provider_prefix, provider_url, status, progress, parameters, message, created, started, finished, updated)
      =
      (%(process_id)s, %(provider_prefix)s, %(provider_url)s, %(status)s, %(progress)s, %(parameters)s, %(message)s, %(created)s, %(started)s, %(finished)s, %(updated)s)
      WHERE job_id = %(job_id)s
    """
    with DBHandler() as db:
      db.run_query(query, query_params=self._to_dict())

  def display(self):
    job_dict = self._to_dict()
    job_dict["type"] = "process"
    job_dict["jobID"] = job_dict.pop("job_id")

    process_id = {
      "process_id": job_dict.pop("process_id"),
      "provider_prefix": self.provider_prefix
    }
    job_dict["processID"] = base64.urlsafe_b64encode(json.dumps(process_id).encode()).decode()
    job_dict["links"] = []

    for attr in job_dict:
      if isinstance(job_dict[attr], datetime):
        job_dict[attr] = job_dict[attr].strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    if self.status in (
      JobStatus.successful.value,
      JobStatus.running.value,
      JobStatus.accepted.value
    ):

        job_result_url = f"{config.server_url}/api/jobs/{self.job_id}/results"

        job_dict['links'] = [{
            'href': job_result_url,
            'rel': 'service',
            'type': 'application/json',
            'hreflang': 'en',
            'title': f'Results of job {self.job_id} as geojson - available when job is finished.'
        }]

    return {k: job_dict[k] for k in self.DISPLAYED_ATTRIBUTES}

  def results(self):
    if self.status == JobStatus.successful.value:
      p = PROVIDERS[self.provider_prefix]
      self.provider_url    = p['url']

      response = requests.get(
          f"{self.provider_url}/jobs/{self.job_id}/results?f=json",
          auth    = (p['user'], p['password']),
          headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        )
      # TODO: manage error
      response.raise_for_status()
      return response.json()
    else:
      return { "error": f"No result available: {response.status_code} - {response.reason}" }

  def __str__(self):
    return f"""
      ----- src.job.Job -----
      job_id={self.job_id}, process_id={self.process_id},
      status={self.status}, message={self.message},
      progress={self.progress}, parameters={self.parameters},
      started={self.started}, created={self.created},
      finished={self.finished}, updated={self.updated}
    """

  def __repr__(self):
    return f'src.job.Job(job_id={self.job_id})'
