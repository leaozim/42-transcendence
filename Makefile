SERVER_CONTAINER_NAME="transcendence-server"

build:
	@echo "[WARNING] SEE IF YOU SETUP DE ENV FILE"
	docker-compose -f ./docker-compose.yml up -d --build

down:
	docker-compose -f ./docker-compose.yml down

clear:
	docker-compose -f ./docker-compose.yml down --rmi all -v

test: build
	docker exec -it ${SERVER_CONTAINER_NAME} sh -c "chmod +x test.sh && ./test.sh"

.PHONY: down clear build

