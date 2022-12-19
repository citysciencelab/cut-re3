CREATE TYPE status AS ENUM ('accepted', 'running', 'successful', 'failed', 'dismissed');

CREATE TABLE IF NOT EXISTS jobs (
  id                 serial,
  job_id             varchar(40),
  process_id         varchar(40),
  status             status,
  message            text,
  progress           integer,
  parameters         json,
  job_start_datetime timestamp,
  job_end_datetime   timestamp,
  CONSTRAINT id PRIMARY KEY(id)
);

GRANT ALL PRIVILEGES ON TABLE jobs TO cut_re3;
GRANT ALL PRIVILEGES ON SEQUENCE jobs_id_seq to cut_re3;
