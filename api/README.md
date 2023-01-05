# OGC Processes API

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
We have two DB users:
- the privileged POSTGRES_USER user configured in geoserver/configs/geoserver
- the user used by the API with privileges on the jobs table (e.g. see api/initializers/db/create_db_user.sh). Its credentials are configured in docker-compose.yml.

docker-compose exec postgis bash
psql -U <username> -d <db_name>

## Environment Variables
|   Variable    | Default value | Description |
| ------------- | ------------- | ----------- |
|  SERVER_URL      | localhost:3000 | This is only used to return the complete URL in the result of the job details as specified in OGC. |

