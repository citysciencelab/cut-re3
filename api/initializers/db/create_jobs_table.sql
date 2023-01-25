CREATE TYPE status AS ENUM ('accepted', 'running', 'successful', 'failed', 'dismissed');

CREATE TABLE IF NOT EXISTS jobs (
  process_id       varchar(40),
  job_id           varchar(40) PRIMARY KEY,
  provider_prefix  varchar(40),
  provider_url     varchar(40),
  status           status,
  message          text,
  created          timestamp,
  started          timestamp,
  finished         timestamp,
  updated          timestamp,
  progress         integer,
  parameters       json,
  results_metadata json
);

GRANT ALL PRIVILEGES ON TABLE jobs TO cut_dev;
