import requests
import config

def all_processes_as_json():
  response = requests.get(
      f"{config.model_platform_url}/processes",
      auth    = ('cut', 'modelplatform'),
      headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    )
  return response.content
