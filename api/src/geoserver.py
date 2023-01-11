import requests
import config
from src.data_helper import convert_data_to_shapefile, archive_data, cleanup_unused_files
from src.errors import GeoserverException
import os
import json
import logging

logging.basicConfig(level=logging.INFO)

class Geoserver:

  RESULTS_FILENAME = "results.geojson"

  def __init__(self):
    self.workspace = config.geoserver_workspace
    self.errors = []
    self.path = None
    self.job_id = None

  def create_workspace(self):
    response = requests.get(
      f"{config.geoserver_workspaces_url}/{self.workspace}.json?quietOnNotFound=True",
      auth    = (config.geoserver_admin_user, config.geoserver_admin_password),
      headers = {'Content-type': 'application/json', 'Accept': 'application/json'},
      timeout = 60
    )

    if response.status_code == 200:
      logging.info(f" --> Workspace {self.workspace} already exists.")
      return True

    if response.status_code == 404:
      logging.info(f" --> Workspace {self.workspace} not found - creating....")
    else:
      raise GeoserverException(
        f"There was an error retrieving workspace {self.workspace}: {response.status_code}: {response.reason} - {response.url}"
      )

    response = requests.post(
      config.geoserver_workspaces_url,
      auth    = (config.geoserver_admin_user, config.geoserver_admin_password),
      data    = f"<workspace><name>{self.workspace}</name></workspace>",
      headers = {'Content-type': 'text/xml', 'Accept': '*/*'}
    )

    if response.ok:
      logging.info(f' --> Created new workspace {self.workspace}.')
    else:
      raise GeoserverException(f"Workspace {self.workspace} could not be created: {response.status_code}: {response.reason}")

  def save_results(self, job_id: str, data: json):
    self.job_id = job_id
    store_name = job_id

    self.path = os.path.join('data', 'geoserver', job_id)
    os.mkdir(self.path)

    # write geojson data to file path/results.geojson
    with open(os.path.join(self.path, self.RESULTS_FILENAME), "x") as file:
      file.write(data)

    self.create_workspace()

    try:
      convert_data_to_shapefile(
        path = self.path,
        filename = self.RESULTS_FILENAME,
        shapefile_name = job_id
      )
    except Exception as e:
      raise GeoserverException(
        f"Received geojson result file could not be converted to shapefile.",
        payload={
          "error": type(e).__name__,
          "message": e
        }
      )

    success = self.push_shapefile_directory(
      store_name = store_name
    )
    if not success:
      return False

    path_to_archive = archive_data(
      path = self.path,
      store_name = store_name
    )

    success = self.push_data_to_store(
      store_name = store_name,
      path_to_archive = path_to_archive
    )
    return success

  def push_shapefile_directory(self, store_name: str):
    xml_config = f"""
    <dataStore>
      <name>{store_name}</name>
      <type>Directory of spatial files (shapefiles)</type>
      <connectionParameters>
        <entry key="charset">ISO-8859-1</entry>
        <entry key="filetype">shapefile</entry>
        <entry key="create spatial index">true</entry>
        <entry key="memory mapped buffer">false</entry>
        <entry key="timezone">America/New_York</entry>
        <entry key="enable spatial index">true</entry>
        <entry key="namespace">http://www.opengeospatial.net/cite</entry>
        <entry key="cache and reuse memory maps">true</entry>
        <entry key="url">file:/opt/geoserver/data_dir/{store_name}</entry>
        <entry key="fstype">shape</entry>
      </connectionParameters>
    </dataStore>
"""

    # TODO: Check the settings, e.g.
    # .   - Coordinate Reference System, e.g. EPSG:4326
    # .   - Bounding Boxes (in UI can be computed automatically from the data)
    # .   - Basic resource info (name, title, abstract)
    # - plus some Layer Settings like WMS (e.g. polygon)

    response = requests.post(
        f"{config.geoserver_workspaces_url}/{self.workspace}/datastores",
        auth    = (config.geoserver_admin_user, config.geoserver_admin_password),
        data   = xml_config,
        headers = {'Content-type': 'text/xml', 'Accept': '*/*'},
        timeout = 60 * 1
      )

    logging.info(f' --> created shapefile directory {store_name}')
    return response.ok

  def push_data_to_store(self, store_name: str, path_to_archive: str):
    logging.info(f" --> Storing data {path_to_archive} to geoserver store {store_name}")

    with open(path_to_archive, 'rb') as archive:
      response = requests.put(
        f"{config.geoserver_workspaces_url}/{self.workspace}/datastores/{store_name}/file.shp",
        auth    = (config.geoserver_admin_user, config.geoserver_admin_password),
        files   = {'file': archive},
        headers = {'Content-type': 'application/zip'}
      )

    if response.ok:
      return True

    logging.error(f" --> Could not add data to store {store_name}! {response.status_code}: {response.reason}")
    return False

  def cleanup(self):
    cleanup_unused_files(
      path          = self.path,
      base_filename = self.job_id
    )
