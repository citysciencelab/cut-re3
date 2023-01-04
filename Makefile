start:
	docker-compose up nginx frontend geoserver api

stop:
	docker-compose down

restart: stop start

install:
	docker-compose build frontend
	docker-compose build api
	docker-compose run --rm frontend npm install
