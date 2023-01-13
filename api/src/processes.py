import json
import requests
import config

def all_processes():
  response = requests.get(
      f"{config.model_platform_url}/processes",
      auth    = ('cut', 'modelplatform'),
      headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    )
  return json.loads(response.content)

def all_processes_as_json():
  result = all_processes()
  return json.dumps(result)
