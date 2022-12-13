start:
	docker-compose up nginx processes

stop:
	docker-compose down

restart: stop start

install:
	docker-compose run --rm frontend npm install
