start: stop
	docker compose -f docker-compose.yaml up -d nginx
	docker compose -f docker-compose.yaml up frontend geoserver api

start_prod: stop
	docker compose -f docker-compose.prod.yaml up -d nginx
	docker compose -f docker-compose.prod.yaml up frontend geoserver api

restart: stop start

stop:
	docker compose down

install:
	docker compose build frontend
	docker compose build api
	docker compose run --rm frontend npm install
	docker compose run --rm api pip install --user --upgrade --no-cache-dir -r requirements.txt

install_prod:
	docker compose -f docker-compose.prod.yaml build frontend
	docker compose -f docker-compose.prod.yaml build api
	docker compose -f docker-compose.prod.yaml run --rm frontend npm install
	docker compose -f docker-compose.prod.yaml run --rm api pip install --user --upgrade --no-cache-dir -r requirements.txt
