import config
import psycopg2 as db
from psycopg2.extras import RealDictCursor
from src.errors import CustomException

import logging

logger = logging.getLogger(__name__)

class DBHandler():
  def __init__(self):
    self.connection = db.connect(
      database = config.postgres_db,
      host     = config.postgres_host,
      user     = config.postgres_user,
      password = config.postgres_password,
      port     = config.postgres_port
    )

  def run_query(self, query, conditions=[], query_params={}, limit=None, page=None):
    if conditions:
      query += " WHERE " + " AND ".join(conditions)

    if limit:
      offset = 0
      if page:
        offset = (page - 1) * limit

      query += " LIMIT %(limit)s OFFSET %(offset)s"
      query_params['limit'] = limit
      query_params['offset'] = offset

    with self.connection:
      with self.connection.cursor(cursor_factory = RealDictCursor) as cursor:
        cursor.execute(query, query_params)
        try:
          results = cursor.fetchall()
        except db.ProgrammingError as e:
          if str(e) == "no results to fetch":
            return
          else:
            raise e

    return results

  # needed so that this class can be used as a context manager
  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    if (self.connection):
      self.connection.close()

    if type is None and value is None and traceback is None:
      return True

    logger.error(f"{type}: {value} - {traceback}")
    return False
