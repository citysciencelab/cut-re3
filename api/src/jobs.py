from enum import Enum
from datetime import datetime

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
  def __init__(self, job_id):
    self.id = job_id
    # TODO: get job from postgreSQL with
    self.process_id ='123'
    self.status = JobStatus.running
    self.message = "bla bla"
    self.progress = 0.5
    self.parameters = {"x": 123, "y": 456, "name": "my_simulation"}
    self.job_start_datetime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    self.job_end_datetime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

  def details(self):
    job_details = {
      'processID': self.process_id,
      'jobID': self.id,
      'status': str(self.status),
      'message': self.message,
      'progress': self.progress,
      'parameters': self.parameters,
      'job_start_datetime': self.job_start_datetime,
      'job_end_datetime': self.job_end_datetime
    }

    if self.status in (
      JobStatus.successful, JobStatus.running, JobStatus.accepted):

        # TODO
        job_result_url = f"{config.server_url}/jobs/{self.id}/results.geojson"  # noqa

        job_details['links'] = [{
            'href': job_result_url,
            'rel': 'about',
            'type': 'application/json',
            'title': f'results of job {self.id} as JSON'
        }]
    return job_details

# TODO: this is only mocked
def all_jobs_as_json():
  with open("example_api_jobs.json") as f:
    result = f.read()
  return result
