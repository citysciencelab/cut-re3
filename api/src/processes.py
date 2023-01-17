import requests
from configs.platforms import platforms
import logging
import base64
import json

def all_processes():
  processes = []
  for prefix in platforms:
    p = platforms[prefix]

    response = requests.get(
        f"{p['url']}/processes",
        auth    = (p['user'], p['password']),
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
      )
    if response.ok:
      results = response.json()
      for process in results["processes"]:
        process_id = {
          "process_id": process['id'],
          "platform_prefix": prefix
        }
        process["id"] = base64.urlsafe_b64encode(json.dumps(process_id).encode()).decode()

      processes += results["processes"]
    else:
      logging.error(f"Processes could not be retrieved from platform {p['url']}!!! {response.status_code}: {response.reason}")

  return { "processes": processes }
