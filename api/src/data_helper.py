from zipfile import ZipFile
import geopandas as gpd
import os
import os.path

APPENDICES = ["cpg", "dbf", "prj", "shx", "shp"]

def convert_data_to_shapefile(path: str, filename: str, shapefile_name: str):
  gdf = gpd.read_file(f"{path}/{filename}")

  shapefile = f"{path}/{shapefile_name}.shp"
  gdf.to_file(shapefile, driver='ESRI Shapefile')

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
