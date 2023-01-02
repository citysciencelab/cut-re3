import os

server_url = os.environ.get("SERVER_URL", "localhost:5001")

postgres_db = os.environ.get("POSTGRES_DB", "cut_dev")
postgres_host = os.environ.get("POSTGRES_HOST", "postgis")
postgres_user = os.environ.get("POSTGRES_USER", "postgres")
postgres_password = os.environ.get("POSTGRES_PASSWORD", "postgres")
postgres_port = os.environ.get("POSTGRES_PORT", 5432)

geoserver_workspace = os.environ.get("GEOSERVER_WORKSPACE", "cut_dev")
