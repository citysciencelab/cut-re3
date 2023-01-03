import geopandas as gpd
import requests
import config
import re
from zipfile import ZipFile
import os

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

  def create_store(self, store_name: str, path: str, filename: str, workspace: str):
    gdf = gpd.read_file(f"{path}/{filename}")

    shapefile = f"{path}/{store_name}.shp"
    gdf.to_file(shapefile, driver='ESRI Shapefile')
    appendices = ["cpg", "dbf", "prj", "shx", "shp"]

    with ZipFile(f"{path}/{store_name}.zip", mode="x") as archive:
      for appendix in appendices:
        archive.write(
          f"{path}/{store_name}.{appendix}",
          arcname=f"{store_name}.{appendix}"
        )

    file = open(f"{path}/{store_name}.zip", 'rb')

    response = requests.put(
      f"http://geoserver:8080/geoserver/rest/workspaces/{workspace}/datastores/{store_name}/file.shp",
      auth    = (config.geoserver_admin_user, config.geoserver_admin_password),
      files   = {'file': file},
      headers = {'Content-type': 'application/zip'}
    )
    appendices.append('zip')
    for appendix in appendices:
      os.remove(f"{path}/{store_name}.{appendix}")

    return response.ok

  def create_layer(self):
    pass

  def save(self, data, workspace):
    print(f"Storing data to geoserver", flush=True)
    job_id = "job_id_123456"
    # path = os.path.join('data', base_filename)
    # os.mkdir(path)

    # workspace could be the process name/id
    workspace = "my_workspace"
    success = self.create_workspace(workspace)
    if success == False:
      raise f"Could not create workspace {workspace}!"

    success = self.create_store(
      store_name = "results_XS",
      path       = f"data/{job_id}",
      filename =   "results_XS.geojson",
      workspace =  workspace
    )

    if success == False:
      raise f"Could not create store."

    success = self.create_layer(

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
