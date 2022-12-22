from datetime import datetime
import uuid
import json
import config
from src.db_handler import DBHandler
from src.job_status import JobStatus

class Job:
  DISPLAYED_ATTRIBUTES = [
      "processID", "type", "jobID", "status", "message",
      "created", "started", "finished", "updated", "progress",
      "links"
    ]

  def __init__(self, job_id=None, process_id=None, parameters={}):
    self.job_id      = job_id
    self.process_id  = process_id
    self.parameters = parameters
    self.status     = None
    self.message    = None
    self.progress   = None
    self.parameters = {}
    self.created    = None
    self.started    = None
    self.finished   = None
    self.updated    = None
    self.errors     = []

    if job_id is not None:
      self._init_from_db(job_id)
    else:
      self._create()

  def _init_from_db(self, job_id):
    query = """
      SELECT * FROM jobs WHERE job_id = %(job_id)s
    """
    db_handler = DBHandler()
    with db_handler as db:
      job_details = db.retrieve(query, {'job_id': job_id})

    if len(job_details) > 0:
      data = job_details[0]

      self._init_from_dict(dict(data))
    else:
      self.errors.append(f"Job with ID={job_id} not found.")

  def _init_from_dict(self, data):
    self.job_id     = data['job_id']
    self.process_id = data['process_id']
    self.type       = "process"
    self.status     = data['status']
    self.message    = data['message']
    self.created    = data['created']
    self.started    = data['started']
    self.finished   = data['finished']
    self.updated    = data['updated']
    self.progress   = data['progress']
    self.parameters = data['parameters']

  def _create(self):
    self.job_id     = str(uuid.uuid4())
    self.status    = JobStatus.accepted.value
    self.progress  = 0
    self.message   = ""
    self.created   = datetime.utcnow() #.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    self.started   = None
    self.updated   = datetime.utcnow() #.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    self.finished  = None

    query = """
      INSERT INTO jobs
      (job_id, process_id, status, progress, parameters, message, created, started, finished, updated)
      VALUES
      (%(job_id)s, %(process_id)s, %(status)s, %(progress)s, %(parameters)s, %(message)s, %(created)s, %(started)s, %(finished)s, %(updated)s)
    """
    db_handler = DBHandler()
    with db_handler as db:
      db.execute(query, self._to_dict())

  def _to_dict(self):
    return {
      "process_id": self.process_id,
      "job_id":     self.job_id,
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
      (process_id, status, progress, parameters, message, created, started, finished, updated)
      =
      (%(process_id)s, %(status)s, %(progress)s, %(parameters)s, %(message)s, %(created)s, %(started)s, %(finished)s, %(updated)s)
      WHERE job_id = %(job_id)s
    """
    db_handler = DBHandler()
    with db_handler as db:
      db.execute(query, self._to_dict())

  def display(self):
    job_dict = self._to_dict()
    job_dict["type"] = "process"
    job_dict["jobID"] = job_dict.pop("job_id")
    job_dict["processID"] = job_dict.pop("process_id")
    job_dict["links"] = []

    for attr in job_dict:
      if isinstance(job_dict[attr], datetime):
        job_dict[attr] = job_dict[attr].strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    if self.status in (
      JobStatus.successful.value, JobStatus.running.value, JobStatus.accepted.value):
        # TODO
        job_result_url = f"{config.server_url}/jobs/{self.job_id}/results.geojson"  # noqa

        job_dict['links'] = [{
            'href': job_result_url,
            'rel': 'service',
            'type': 'application/json',
            'hreflang': 'en',
            'title': f'results of job {self.job_id} as JSON'
        }]

    return {k: job_dict[k] for k in self.DISPLAYED_ATTRIBUTES}

  def delete():
    raise Exception(f'******* Deleting job not implemented!')

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

def all_jobs():
  jobs = []
  query = """
    SELECT job_id FROM jobs
  """
  db_handler = DBHandler()
  with db_handler as db:
    job_ids = db.retrieve(query, {})

  for row in job_ids:
    job = Job(row['job_id'])
    jobs.append(job.display())

  return { "jobs": jobs }
