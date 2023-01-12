from src.db_handler import DBHandler
from src.job_status import JobStatus
from src.job import Job

DEFAULT_LIMIT = 10

def get_jobs(args):
  page  = args["page"] if "page" in args else 1
  limit = args["limit"] if "limit" in args else DEFAULT_LIMIT

  jobs = []
  query = """
    SELECT job_id FROM jobs
  """
  query_params = {}
  conditions = []

  if 'processID' in args and args['processID']:
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

  db_handler = DBHandler()
  db_handler.set_sortable_columns(Job.SORTABLE_COLUMNS)
  with db_handler as db:
    job_ids = db.run_query(query,
      conditions   = conditions,
      query_params = query_params,
      order        = ['created'],
      limit        = limit,
      page         = page
    )

  for row in job_ids:
    job = Job(row['job_id'])
    jobs.append(job.display())

  count_jobs = count(conditions, query_params)
  links = next_links(page, limit, count_jobs)

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

def count(conditions, query_params):
  count_query = """
    SELECT count(*) FROM jobs
  """
  db_handler = DBHandler()
  with db_handler as db:
    count_jobs = db.run_query(
      count_query,
      conditions=conditions,
      query_params=query_params
    )
  return count_jobs[0]['count']


