# Process API

## API documentation
This API implements the OGC processes standard (except that it is not complete). E.g. there is no html landingpage implemented, only the API.

For an API description e.g. for the jobs list see:
https://docs.ogc.org/is/18-062r2/18-062r2.html#rc_job-list
or
https://developer.ogc.org/api/processes/index.html#tag/JobList

For convenience there is still some documentation below.

### GET api/jobs
Example payload:
{
    "limit": 15,
    "page": 2,
    "processID": ["model1", "model2"],
    "status": ["running", "successful"]
}

Default limit = 10
Payload may also be empty.

## Access DB
docker-compose exec db bash
psql -U cut_dev -d cut_dev
