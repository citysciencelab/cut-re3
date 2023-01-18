import requests
import logging
import base64
import json
import yaml

PROVIDERS = yaml.safe_load(open('./configs/providers.yml'))

def all_processes():
  processes = []
  for prefix in PROVIDERS:
    p = PROVIDERS[prefix]

    try:
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
            "provider_prefix": prefix
          }
          process["id"] = base64.urlsafe_b64encode(json.dumps(process_id).encode()).decode()

        processes += results["processes"]
      else:
        logging.error(f"Processes could not be retrieved from provider {p['url']}!!! {response.status_code}: {response.reason}")

    except Exception as e:
      logging.error(f"Could not connect to {p['url']}:")
      logging.error(e)
      logging.error("Please fix entries in providers.yml!!!")

  return { "processes": processes }
