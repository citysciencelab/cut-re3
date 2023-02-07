start: stop
	docker-compose -f docker-compose.yaml up -d nginx
	docker-compose -f docker-compose.yaml up frontend geoserver api

start_prod: stop
	docker-compose -f docker-compose.prod.yaml up -d nginx
	docker-compose -f docker-compose.prod.yaml up frontend geoserver api

restart: stop start

stop:
	docker-compose down

clean: stop
	docker-compose run --rm frontend rm -rf node_modules
	docker-compose run --rm helper rm -rf /workspace/api
	docker-compose run --rm helper rm -rf /workspace/geoserver

install:
	docker-compose build frontend
	docker-compose build api
	docker-compose run --rm frontend npm install
	docker-compose run --rm api pip install --user --upgrade --no-cache-dir -r requirements.txt
