import json
import time
import logging
from src.job import Job, JobStatus
from src.geoserver import Geoserver
from multiprocessing import dummy
from datetime import datetime
from src.processes import all_processes
import config

logger = logging.getLogger(__name__)

class Process():
  def __init__(self, process_id=None):
    self.process_id = process_id
    self.process = self.set_details()

  def set_details(self):
    processes = all_processes()

    for process in processes["processes"]:
      if process['id'] == self.process_id:
        return process

    raise InvalidParamsException("Process ID unknown!")

  def execute(self, parameters):
    self.validate_params(parameters)

    job = Job(job_id=None, process_id=self.process_id, parameters=parameters)
    logger.info(f"Executing {self.process_id} with params {parameters}")

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

    print(f'******* execute started in backend with params {parameters}', flush=True)
    time.sleep(3)
    i = 3
    print(f'******* still running', flush=True)
    time.sleep(3)
    i += 3
    print(f'******* still running', flush=True)

    geoserver = Geoserver()
    with open("data/job_id_123456/results_XS.geojson") as f:
      results = f.read()
      geoserver.save(
        data=results,
        workspace=config.geoserver_workspace
      )

    time.sleep(3)
    i += 3
    print(f'******* finished', flush=True)

    job.finished = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    job.status = JobStatus.successful.value
    job.progress = 100
    job.save()

    # TODO
    # write results to geocoder
    # read the results from there when delivering jobs result in jobs.py
    # wait and check result: update job.progress

  def validate_params(self, params={}):
    for input in self.process['inputs'].keys():
      if self.process['inputs'][input]["minOccurs"] > 0 and params.get(input) is None:
        # TODO should this be a bad request?
        raise InvalidParamsException(f'Cannot process without parameter {input}')

  def to_json(self):
    return json.dumps(self, default=lambda o: o.__dict__,
      sort_keys=True, indent=2)

  def __str__(self):
    return f'src.process.Process object: process_id={self.process_id}'

  def __repr__(self):
    return f'src.process.Process(process_id={self.process_id})'

class InvalidParamsException(Exception):
  pass
