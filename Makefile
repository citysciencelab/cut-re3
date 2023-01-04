start:
	docker-compose up nginx processes frontend geoserver

stop:
	docker-compose down

restart: stop start

install:
	docker-compose build frontend
	docker-compose build processes
	docker-compose run --rm frontend npm install
