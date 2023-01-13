import json
import time
import re
import logging
from src.job import Job, JobStatus
from src.geoserver import Geoserver
from multiprocessing import dummy
from datetime import datetime
from src.processes import all_processes
import logging
import config
import requests
from werkzeug.exceptions import HTTPException

logging.basicConfig(level=logging.INFO)

class Process():
  def __init__(self, process_id=None):
    self.process_id = process_id
    self.process = self.set_details()
    for key in self.process:
      setattr(self, key, self.process[key])

  def set_details(self):
    processes = all_processes()

    for process in processes["processes"]:
      if process['id'] == self.process_id:
        return process

    raise InvalidParamsException("Process ID unknown!")

  def execute(self, parameters):
    self.validate_params(parameters)

    job = self.start_process_execution(parameters)

    _process = dummy.Process(
            target=self._wait_for_results,
            args=([job])
        )
    _process.start()

    result = {
      "job_id": job.job_id,
      "status": job.status
    }
    return result

  def start_process_execution(self, parameters):
    params = parameters
    params["mode"] = "async"
    logging.info(f" --> Executing {self.process_id} with params {params}")

    # TODO model_platform_url has to come from the list of processes
    # maybe process.url ?
    response = requests.post(
        f"{config.model_platform_url}/processes/{self.process_id}/execution",
        json    = params,
        auth    = ('cut', 'modelplatform'),
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
      )

    if response.ok and response.headers:
      match = re.search('http.*/jobs/(.*)$', response.headers["location"])
      if match:
        job_id = match.group(1)

      job = Job(job_id=job_id, process_id=self.process_id, parameters=params)
      job.started = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
      job.status = JobStatus.running.value
      job.save()

      return job

  def _wait_for_results(self, job):
    finished = False
    timeout = 60 * 3
    start = time.time()

    # TODO: credentials
    while not finished:
      response = requests.get(
          f"{config.model_platform_url}/jobs/{job.job_id}",
          auth    = ('cut', 'modelplatform'),
          headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        )
      response.raise_for_status()

      job_details = response.json()

      # Remark: doesn't the OGC specification ask for a "finished" timestamp
      # to be returned instead?
      if job_details["job_end_datetime"]:
        finished = True

      if time.time() - start > timeout:
        raise TimeoutError(f"Job did not finish within {timeout/60} minutes. Giving up.")

    logging.info(f" --> Remote execution job {job.job_id}: success = {finished}. Took approx. {int((time.time() - start)/60)} minutes.")

    if job_details["status"] != JobStatus.successful.value:
      job.status = JobStatus.failed.value
      job.finished = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
      job.updated = job.finished
      job.progress = 100
      job.message = f'Remote execution was not successful! {job_details["message"]}'
      job.save()
      # TODO CustomException
      raise Exception(f"Remote job {job} could not be successfully executed!")

    geoserver = Geoserver()

    response = requests.get(
        f"{config.model_platform_url}/jobs/{job.job_id}/results?f=json",
        auth    = ('cut', 'modelplatform'),
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
      )
    response.raise_for_status()

    results = response.json()

    geoserver.save_results(
      job_id    = job.job_id,
      data      = results
    )

    if geoserver.errors:
      logging.error(f" --> Could not store data to geoserver: {', '.join(geoserver.errors)}")
    else:
      logging.info(f" --> Successfully stored results to geoserver.")

    geoserver.cleanup()

    job.finished = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    job.status = JobStatus.successful.value
    job.progress = 100
    job.save()

    # TODO
    # read the results from there when delivering jobs result in jobs.py
    # wait and check result: update job.progress

  def validate_params(self, params={}):
    pass
    # for input in self.process['inputs'].keys():
    #   if self.process['inputs'][input]["minOccurs"] > 0 and params.get(input) is None:
    #     # TODO should this be a bad request?
    #     raise InvalidParamsException(f'Cannot process without parameter {input}')

  def to_json(self):
    return json.dumps(self.process, default=lambda o: o.__dict__,
      sort_keys=True, indent=2)

  def __str__(self):
    return f'src.process.Process object: process_id={self.process_id}'

  def __repr__(self):
    return f'src.process.Process(process_id={self.process_id})'

class InvalidParamsException(Exception):
  pass
