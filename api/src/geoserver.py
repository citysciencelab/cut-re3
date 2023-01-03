import geopandas as gpd
import requests
import config
import re
from zipfile import ZipFile

class Geoserver:

  def __init__(self):
    pass

  def create_workspace(self, workspace):
    response = requests.get(
      f"http://geoserver:8080/geoserver/rest/workspaces/{workspace}.json?quietOnNotFound=True",
      auth    = (config.geoserver_admin_user, config.geoserver_admin_password),
      headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    )
    if response:
      print(f"Workspace {workspace} already exists.", flush=True)
      return

    response = requests.post(
      "http://geoserver:8080/geoserver/rest/workspaces",
      auth    = (config.geoserver_admin_user, config.geoserver_admin_password),
      data    = f"<workspace><name>{workspace}</name></workspace>",
      headers = {'Content-type': 'text/xml', 'Accept': '*/*'}
    )
    return response.ok

  def create_store(self, store_name: str, filename: str, workspace: str):
    gdf = gpd.read_file(filename)

    base_filename = re.match('data/(.*)\.geojson', filename).group(1)
    shapefile = f"data/{base_filename}.shp"
    gdf.to_file(shapefile)

    with ZipFile(f"{base_filename}.zip", mode="x") as archive:
      archive.write(shapefile)

    file = open(f"data/{base_filename}.zip", 'rb')

    response = requests.put(
      f"http://geoserver:8080/geoserver/rest/workspaces/{workspace}/datastores/{base_filename}/file.shp",
      auth    = (config.geoserver_admin_user, config.geoserver_admin_password),
      files   = {'file': file},
      headers = {'Content-type': 'application/zip'}
    )

    return response.ok

  def save(self, data, workspace):
    print(f"Storing data to geoserver", flush=True)

    workspace = "Blabla3t43t"
    success = self.create_workspace(workspace)
    if success == False:
      raise f"Could not create workspace {workspace}!"

    success = self.create_store(
      store_name = "process_id",
      filename =   "data/results_XS.geojson",
      workspace =  workspace
    )

    # for each process we need to create an own workspace
    # or even for each job (not sure)
    # 1. create a workspace
    # 2. create a store with read_only = True (to avoid Geoserver to use locks on the data)
    # 3. on the new layer page click publish
    # 4. For the new layer some settings are mandatory:
    # .   - Coordinate Reference System, e.g. EPSG:4326
    # .   - Bounding Boxes (in UI can be computed automatically from the data)
    # .   - Basic resource info (name, title, abstract)
    # - plus some Layer Settings like WMS (e.g. polygon)

  def layers(self):
    username = "admin"
    password = "password"
    url = "http://geoserver:8080/geoserver/rest/layers.json"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    response = requests.get(url, auth=(username, password), headers=headers)
    return response.json()
