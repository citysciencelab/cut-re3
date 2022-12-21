import config
import psycopg2 as db
from psycopg2.extras import RealDictCursor

import logging

logger = logging.getLogger(__name__)

class DBHandler():
  def __init__(self):
    try:
      self.connection = db.connect(
        database = config.postgres_db,
        host     = config.postgres_host,
        user     = config.postgres_user,
        password = config.postgres_password,
        port     = config.postgres_port
      )
    except (Exception, db.Error) as error:
      print("Error while connecting to PostgreSQL", error, flush=True)
      raise error

  def retrieve(self, query, params):
    # wraps a transaction, but does not close the connection:
    with self.connection:
      with self.connection.cursor(cursor_factory = RealDictCursor) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

  def execute(self, query, params):
    with self.connection:
      with self.connection.cursor(cursor_factory = RealDictCursor) as cursor:
        cursor.execute(query, params)

  # so that this class can be used as a context manager
  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    if (self.connection):
      self.connection.close()

    if type is None and value is None and traceback is None:
      return True

    logger.error(f"{type}: {value} - {traceback}")
    return False
