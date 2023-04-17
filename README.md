# CUT Prototype Urban Model Platform and Masterportal Simulation Controller
The repository for the Masterportal addons and the OGC API Processes Backend
that are developed for the third real world experiment in the CUT project.
In the future, this will also be the place where the participatory model will
be hosted.

This project includes the following components:
- PostGis database
- Geoserver (see https://geoserver.org/)
- Simulation frontend as Masterportal addon
- Backend REST api

The backend api provides endpoints to trigger simulation runs on previously configured remote simulation model servers.

Once a simulation run is finished the geojson results get stored to the PostGis database. From there the data gets imported to the Geoserver and is available for the frontend.

In the frontend a user may start a simulation with custom parameters (as specified by the model). After the results arrive they can be displayed on a map.

## Prerequisites
- Docker

## Setup Development
The components are configured in a docker-compose setup with nginx as a proxy.

After you added the below configurations you can install and start the application with

```
make install
make start
```

There are also
```
make restart
make stop
```
commands available (see Makefile).

## Geoserver configuration
The Geoserver uses two configuration files:
- geoserver/configs/geoserver
- geoserver/configs/postgis

Please copy and adapt the example files from geoserver/configs/geoserver.example and postgis.example. The example files include example values for a development setup.

Currently all results are stored to the Geoserver in a single workspace (e.g. "CUT"). The stores and layers are named by their job ids with the prefix "job-".

The workspace name is configured by the backend api but also has to be configured by the frontend.

The geoserver stores its data into the folder geoserver/data/geoserver. This is configured in the docker-compose.yaml file.

## PostGis configuration
PostGis is configured in geoserver/configs/postgis. The api also loads these env variables by loading geoserver/configs/postgis in the docker-compose files.

The data is stored in geoserver/data/pg_data as configured in docker-compose.yaml (development) and docker-compose.prod.yaml (production). If you want to run development and production on the same server, the data should be written to separate paths.

## nginx configuration
The nginx configuration can be found at nginx/default.conf. It configures the paths to the respective endpoints.
There are no changes necessary for development.

## Backend api configuration
- api/configs/dev_environment
- api/configs/providers.yml

Both configuration files have example files in the api/configs folder.

The **dev_environment** file is loaded by docker-compose. In a production environment you can create a prod_environment file with your settings and use it instead of the dev_environment setting in docker-compose. The dev_environment.example file can be copied over as is for development.

The **providers** file sets up the remote simulation model servers. The implemented backend loads **all** models (= processes) from the configured simulation model servers except the ones explicitely excluded.

The simulation model servers have to provide endpoints that comply with the OGC processes api standard in order to be loaded from this api (see https://ogcapi.ogc.org/processes/). Otherwise they will be silently ignored. An error will be logged.

In case the **providers** file needs to be modified, the server has to be restarted (make restart).

## Frontend configuration
- frontend/portal/simulation/config.js
- frontend/portal/simulation/resources/services-internet.json

In the **config.js** file configure the url to the Geoserver results as "simulationGeoserverWorkspaceUrl" in the form \<url to geoserver>/\<workspace name>/ows. The current settings use localhost as configured in the nginx configuration (see nginx/default.conf). Also provide the url to the backend api as "simulationApiUrl".

The current settings in **config.js** can be kept as is for a development setup.

The frontend can be configured to provide a selected list of simulation models (= processes) provided by the backend api.

Please configure the process IDs in **services-internet.json** as "simModelId". The list of available process IDs is provided by the backend endpoint \<base url>/api/processes.

Also configure the correct URL to the Geoserver in **services-internet.json** as "url".

### Production Container

A production ready container for the frontend is configured under `frontend_prod` in the docker-compose file. Run `docker-compose build frontend_prod` to create this container which includes a production build of the frontend portal files. The command `docker-compose up frontend_prod` will serve the portal on the defined port.

## Routes
If not configured differently in nginx/default.conf, then:

The **frontend** is available under localhost:3000. Click on the link "portal" -> "simulation" and then choose "Werkzeuge" -> "Simulation Tool".

The **Geoserver** is available under localhost:3000/geoserver. Choose "Layer previews" in the menu to see the list of uploaded layers. If you click on OpenLayers then the data will be displayed in a new tab.

The **backend api** is available under localhost:3000/api.

## Deployment
After configurations are done for production, for deployment you can run
```
make install_prod
make start_prod
```
It will use the provided docker-compose.prod.yaml file together with the nginx default.conf settings.

## Reset data in development
If you are in development and want to reset all PostGis and Geoserver data, you can safely delete the geoserver/data folder completely.


