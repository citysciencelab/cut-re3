start:
	docker-compose up nginx frontend

stop:
	docker-compose down

restart: stop start

install:
	docker-compose run --rm frontend npm install
