all:
	echo "[WARNING] SEE IF YOU SETUP DE ENV FILE"
	PWD=$$PWD docker-compose -f ./docker-compose.yml up -d --build

down:
	docker-compose -f ./docker-compose.yml down

clear:
	docker-compose -f ./docker-compose.yml down --rmi all -v

.PHONY: all down clear

