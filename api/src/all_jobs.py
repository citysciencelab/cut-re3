from src.db_handler import DBHandler
from src.job_status import JobStatus
from src.job import Job

def all_jobs(args):
  jobs = []
  query = """
    SELECT job_id FROM jobs
  """
  query_params = {}
  conditions = []

  if 'processID' in args:
    conditions.append("process_id IN %(process_id)s")
    query_params['process_id'] = tuple(args['processID'])

  if 'status' in args:
    query_params['status'] = tuple(args['status'])
  else:
    query_params['status'] = (
      JobStatus.running.value, JobStatus.successful.value,
      JobStatus.failed.value, JobStatus.dismissed.value
    )
  conditions.append("status IN %(status)s")

  # TODO for OGC standard: datetime, minDuration, maxDuration parameters

  job_ids = run_db_query(query, conditions, query_params, args['limit'], args['page'])

  for row in job_ids:
    job = Job(row['job_id'])
    jobs.append(job.display())

  count_jobs = count_requested_jobs(conditions, query_params)
  links = next_links(args['page'], args['limit'], count_jobs)

  return { "jobs": jobs, "links": links, "total_count": count_jobs }

def next_links(page, limit, count_jobs):
  if count_jobs <= limit:
    return []

  links = []
  if count_jobs > (page - 1) * limit:
    links.append({
      "href": f"/api/jobs?page={page+1}&limit={limit}",
      "rel": "service",
      "type": "application/json",
      "hreflang": "en",
      "title": f"Next page of jobs."
    })

  if page > 1:
    links.append({
      "href": f"/api/jobs?page={page-1}&limit={limit}",
      "rel": "service",
      "type": "application/json",
      "hreflang": "en",
      "title": f"Previous page of jobs."
    })

  return links

def count_requested_jobs(conditions, query_params):
  count_query = """
    SELECT count(*) FROM jobs
  """
  count_jobs = run_db_query(count_query, conditions, query_params)
  return count_jobs[0]['count']

def run_db_query(query, conditions, query_params, limit=None, page=None):
  query += " WHERE " + " AND ".join(conditions)

  if limit:
    offset = 0
    if page:
      offset = (page - 1) * limit

    query += " LIMIT %(limit)s OFFSET %(offset)s"
    query_params['limit'] = limit
    query_params['offset'] = offset

  db_handler = DBHandler()
  with db_handler as db:
    result = db.retrieve(query, query_params)

  print(f'******* result = {result}', flush=True)
  return result

