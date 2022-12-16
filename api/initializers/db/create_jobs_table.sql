CREATE TYPE status AS ENUM ('accepted', 'running', 'successful', 'failed', 'dismissed');

CREATE TABLE IF NOT EXISTS jobs (
  id                 serial,
  job_id             varchar(40),
  process_id         integer,
  status             status,
  message            text,
  progress           integer,
  parameters         json,
  job_start_datetime timestamp,
  job_end_datetime   timestamp,
  CONSTRAINT id PRIMARY KEY(id)
)
