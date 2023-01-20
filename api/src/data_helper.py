from zipfile import ZipFile
import geopandas as gpd
import os
import os.path
import geopandas as gpd
from sqlalchemy import create_engine
import configs.config as config

APPENDICES = ["cpg", "dbf", "prj", "shx", "shp"]

def geojson_to_postgis(path: str, filename: str, table_name: str):
  #engine = create_engine('postgresql://cut_dev:postgres@postgis/cut_dev')
  engine = create_engine(f'postgresql://{config.postgres_user}:{config.postgres_password}@postgis/{config.postgres_db}')
  gdf = gpd.read_file(f"{path}/{filename}")
  gdf.to_postgis(name=table_name, con=engine)

def convert_data_to_shapefile(path: str, filename: str, shapefile_name: str):
  gdf = gpd.read_file(f"{path}/{filename}")

  shapefile = f"{path}/{shapefile_name}.shp"
  gdf.to_file(shapefile, driver='ESRI Shapefile')

def convert_to_kml(path: str, filename: str, output_filename: str):
  gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
  gdf = gpd.read_file(f"{path}/{filename}")

  kml_file = f"{path}/{output_filename}.kml"
  gdf.to_file(kml_file, driver='KML')

def archive_data(path: str, store_name: str):
  with ZipFile(f"{path}/{store_name}.zip", mode="x") as archive:
    for appendix in APPENDICES:
      archive.write(
        f"{path}/{store_name}.{appendix}",
        arcname=f"{store_name}.{appendix}"
      )
  return f"{path}/{store_name}.zip"

def cleanup_unused_files(path, base_filename):
  for appendix in APPENDICES:
    filename = os.path.join(path, f"{base_filename}.{appendix}")
    if os.path.exists(filename):
      os.remove(filename)
