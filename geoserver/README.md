# Geoserver

If you want to connect the Geoserver to the PostGis database: these are the settings you will have to use when creating a "store" within the Geoserver UI:

Data Source Name: name of the table you want to connect to.
host: postgis
port: 5432
database: cut_dev
schema: public
user: postgres
passwd: postgres

See configs in config files.

Keep the defaults for everything else.
