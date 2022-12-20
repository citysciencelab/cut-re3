import json
import time
import logging
from src.job import Job
from multiprocessing import dummy

logger = logging.getLogger(__name__)

class Process():
  def __init__(self, process_id=None):
    self.process_id = process_id
    self.process = self.set_details()

  def set_details(self):
    processes = _all_processes()

    for process in processes["processes"]:
      if process['id'] == self.process_id:
        return process

    raise InvalidParamsException("Process ID unknown!")

  def execute(self, params):
    self.validate_params(params)

    job = Job(job_id=None, process_id=self.process_id, params=params)
    logger.info(f"Executing {self.process_id} with params {params}")

    _process = dummy.Process(
            target=self._execute_in_backend,
            args=([job, params])
        )
    _process.start()

    result = {
      "job_id": job.job_id,
      "status": job.status
    }
    return result

  def _execute_in_backend(self, job, params):
    print(f'******* execute started in backend with params {params}', flush=True)
    time.sleep(3)
    i = 3
    print(f'******* still running', flush=True)
    time.sleep(3)
    i += 3
    print(f'******* still running', flush=True)

    with open("data/results_XS.geojson") as f:
      results = f.read()

    # TODO
    # write results to geocoder
    # read the results from there when delivering jobs result in jobs.py
    # wait and check result: update job.progress

    print(f'***** execute_sync finished', flush=True)

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

def _all_processes():
  with open("example_processes_list.json") as f:
    result = f.read()
  return json.loads(result)

def all_processes_as_json():
  result = _all_processes()
  return json.dumps(result)

class InvalidParamsException(Exception):
  pass
