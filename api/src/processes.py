import requests
import configs.config as config

def all_processes_as_json():
  response = requests.get(
      f"{config.model_platform_url}/processes",
      auth    = (config.model_platform_user, config.model_platform_password),
      headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    )
  return response.content
