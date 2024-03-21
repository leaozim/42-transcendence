SERVER_CONTAINER_NAME="server"

build:
	@echo "[WARNING] SEE IF YOU SETUP DE ENV FILE"
	docker-compose -f ./docker-compose.yml up -d --build

down:
	docker-compose -f ./docker-compose.yml down

clear:
	docker-compose -f ./docker-compose.yml down --rmi all -v

test: build
	docker exec -i ${SERVER_CONTAINER_NAME} sh -c "python manage.py makemigrations && python manage.py migrate"
	docker exec -i ${SERVER_CONTAINER_NAME} sh -c "./test.sh"


.PHONY: down clear build

