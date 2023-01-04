import json

def all_processes():
  with open("example_processes_list.json") as f:
    result = f.read()
  return json.loads(result)

def all_processes_as_json():
  result = all_processes()
  return json.dumps(result)
