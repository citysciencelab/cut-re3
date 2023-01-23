import json
import time
from datetime import datetime
import re
from multiprocessing import dummy
import requests
import base64
import yaml

from src.job import Job, JobStatus
from src.geoserver import Geoserver
from src.errors import InvalidUsage, CustomException

PROVIDERS = yaml.safe_load(open('./configs/providers.yml'))

import logging

logging.basicConfig(level=logging.INFO)

class Process():
  def __init__(self, process_id_base64=None):
    self.process_id_base64 = process_id_base64

    try:
      process_id_dict = json.loads(base64.urlsafe_b64decode(process_id_base64.encode()).decode())
    except Exception as e:
      raise CustomException(f"Unknown process ID. Get a list of available processes under /api/processes. Error: \"{e}\"")

    self.provider_prefix = process_id_dict['provider_prefix']
    self.process_id = process_id_dict['process_id']
    self.set_details()

  def set_details(self):
    p = PROVIDERS[self.provider_prefix]

    response = requests.get(
      f"{p['url']}/processes/{self.process_id}",
      auth    = (p['user'], p['password']),
      headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    )
    response.raise_for_status()

    if response.ok:
      process_details = response.json()
      for key in process_details:
        setattr(self, key, process_details[key])
    else:
      raise InvalidUsage(f"Model/process not found! {response.status_code}: {response.reason}. Check /api/processes endpoint for available models/processes.")

  def execute(self, parameters):
    p = PROVIDERS[self.provider_prefix]

    # TODO
    # self.validate_params(parameters)

    logging.info(f" --> Executing {self.process_id} on model server {p['url']} with params {parameters} as process {self.process_id_base64}")

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
    p = PROVIDERS[self.provider_prefix]

    response = requests.post(
        f"{p['url']}/processes/{self.process_id}/execution",
        json    = params,
        auth    = (p['user'], p['password']),
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
      )
    response.raise_for_status()

    if response.ok and response.headers:
      match = re.search('http.*/jobs/(.*)$', response.headers["location"])
      if match:
        job_id = match.group(1)

      job = Job(job_id=job_id, process_id_base64=self.process_id_base64, parameters=params)
      job.started = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
      job.status = JobStatus.running.value
      job.save()

      logging.info(f' --> Job {job.job_id} for model {self.process_id_base64} started running.')

      return job

  def _wait_for_results(self, job):
    finished = False
    p = PROVIDERS[self.provider_prefix]
    timeout = float(p['timeout'])
    start = time.time()

    try:
      while not finished:
        response = requests.get(
            f"{p['url']}/jobs/{job.job_id}",
            auth    = (p['user'], p['password']),
            headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
          )
        response.raise_for_status()

        job_details = response.json()

        # Remark: doesn't the OGC specification ask for a "finished" timestamp
        # to be returned instead?
        if job_details["job_end_datetime"]:
          finished = True

        job.progress = job_details["progress"] - 25 # because we still need to store it to geoserver
        job.updated = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        job.save()

        if time.time() - start > timeout:
          raise TimeoutError(f"Job did not finish within {timeout/60} minutes. Giving up.")

      logging.info(f" --> Remote execution job {job.job_id}: success = {finished}. Took approx. {int((time.time() - start)/60)} minutes.")

    except Exception as e:
      logging.error(f" --> Could not retrieve results for job {self.process_id_base64} (={self.process_id})/{job.job_id} from simulation model server: {e}")
      job.status = JobStatus.failed.value
      job.message = str(e)
      job.updated = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
      job.finished = job.updated
      job.progress = 100
      job.save()
      raise CustomException("Could not retrieve results from simulation model server. {e}")

    try:
      if job_details["status"] != JobStatus.successful.value:
        job.status = JobStatus.failed.value
        job.finished = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        job.updated = job.finished
        job.progress = 100
        job.message = f'Remote execution was not successful! {job_details["message"]}'
        job.save()
        raise CustomException(f"Remote job {job} could not be successfully executed! {job.message}")

      geoserver = Geoserver()

      response = requests.get(
          f"{p['url']}/jobs/{job.job_id}/results?f=json",
          auth    = (p['user'], p['password']),
          headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        )
      response.raise_for_status()

      if not response.ok:
        job.status = JobStatus.failed.value
        job.message = f'Could not retrieve results for {job}! {response.status_code}: {response.reason}'

      results = response.json()

      geoserver.save_results(
        job_id    = job.job_id,
        data      = results
      )

      logging.info(f" --> Successfully stored results for job {self.process_id_base64} (={self.process_id})/{job.job_id} to geoserver.")
      job.status = JobStatus.successful.value

    except CustomException as e:
      logging.error(f" --> Could not store results for job {self.process_id_base64} (={self.process_id})/{job.job_id} to geoserver: {e}")
      job.status = JobStatus.failed.value
      job.message = str(e)

    job.finished = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    job.updated = job.finished
    job.progress = 100
    job.save()

    geoserver.cleanup()

  def to_dict(self):
    process_dict = self.__dict__
    process_dict.pop("process_id")
    process_dict.pop("provider_prefix")
    process_dict["id"] = process_dict.pop("process_id_base64")
    return process_dict

  def to_json(self):
    return json.dumps(self.to_dict(), default=lambda o: o.__dict__,
      sort_keys=True, indent=2)

  def __str__(self):
    return f'src.process.Process object: process_id={self.process_id}, process_id_base64={self.process_id_base64}, provider_prefix={self.provider_prefix}'

  def __repr__(self):
    return f'src.process.Process(process_id={self.process_id})'
