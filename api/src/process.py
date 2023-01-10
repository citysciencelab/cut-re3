import json
import time
import logging
from src.job import Job, JobStatus
from src.geoserver import Geoserver
from multiprocessing import dummy
from datetime import datetime
from src.processes import all_processes
from src.errors import InvalidUsage

import logging

logging.basicConfig(level=logging.INFO)

class Process():
  def __init__(self, process_id=None):
    self.process_id = process_id
    self.process = self.set_details()

  def set_details(self):
    processes = all_processes()

    for process in processes["processes"]:
      if process['id'] == self.process_id:
        return process

    raise InvalidUsage("Process ID unknown! Please choose a valid model name as process ID. Check /api/processes endpoint.")

  def execute(self, parameters):
    self.validate_params(parameters)

    logging.info(f" --> Executing {self.process_id} with params {parameters}")

    job = Job(job_id=None, process_id=self.process_id, parameters=parameters)
    job.status = JobStatus.accepted.value
    job.save()

    _process = dummy.Process(
            target=self._execute_in_backend,
            args=([job, parameters])
        )
    _process.start()

    result = {
      "job_id": job.job_id,
      "status": job.status
    }
    return result

  def _execute_in_backend(self, job, parameters):
    job.started = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    job.status = JobStatus.running.value
    job.save()

    time.sleep(3)
    logging.info(f' --> Job {job.job_id} started running at {job.started}')

    # response = requests.get(
    #   config.dummy_model_url,
    #   headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    # )

    geoserver = Geoserver()
    with open("data/job_id_123456/results_XS.geojson") as f:
      results = f.read()

      geoserver.save_results(
        job_id    = job.job_id,
        data      = results
      )

    if geoserver.errors:
      logging.error(f" --> Could not store results for job {job.job_id} to geoserver: {', '.join(geoserver.errors)}")
    else:
      logging.info(f" --> Successfully stored results for job {job.job_id} to geoserver.")

    geoserver.cleanup()

    job.finished = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    if geoserver.errors:
      job.status = JobStatus.failed.value
    else:
      job.status = JobStatus.successful.value
    job.progress = 100
    job.save()

  def validate_params(self, params={}):
    for input in self.process['inputs'].keys():
      if self.process['inputs'][input]["minOccurs"] > 0 and params.get(input) is None:
        raise InvalidUsage(f'Cannot process without parameter {input}')

  def to_json(self):
    return json.dumps(self, default=lambda o: o.__dict__,
      sort_keys=True, indent=2)

  def __str__(self):
    return f'src.process.Process object: process_id={self.process_id}'

  def __repr__(self):
    return f'src.process.Process(process_id={self.process_id})'
