start: stop
	docker-compose -f docker-compose.yaml up -d nginx
	docker-compose -f docker-compose.yaml up frontend geoserver api

start_prod: stop
	docker-compose -f docker-compose.prod.yaml up -d nginx
	docker-compose -f docker-compose.prod.yaml up frontend geoserver api

restart: stop start

stop:
	docker-compose down

install:
	docker-compose build frontend
	docker-compose build api
	docker-compose run --rm frontend npm install
