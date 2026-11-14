# Native (Docker-free) workflow. Works on a plain VM or in a sandbox:
# only Python 3.10-3.12 is required.

VENV     ?= $(CURDIR)/.venv
export VENV

DATA_DIR := $(CURDIR)/data
PID_FILE := $(DATA_DIR)/server.pid
LOG_FILE := $(DATA_DIR)/server.log

# Default target, same as before: install and start in the background.
build: setup start

help:
	@echo "make setup   - create .venv, install requirements, create .env"
	@echo "make run     - run the server in the foreground (Ctrl+C to stop)"
	@echo "make start   - run the server in the background (logs: data/server.log)"
	@echo "make stop    - stop the background server"
	@echo "make logs    - follow the background server logs"
	@echo "make test    - run the test suite with coverage"
	@echo "make build   - setup + start (old 'docker-compose up -d --build')"
	@echo "make down    - alias for stop"
	@echo "make clear   - stop and delete .venv and data/ (database included)"

setup:
	@./scripts/setup.sh

run:
	@./scripts/start.sh

start:
	@mkdir -p $(DATA_DIR)
	@if [ -f $(PID_FILE) ] && kill -0 "$$(cat $(PID_FILE))" 2>/dev/null; then \
		echo "Already running (pid $$(cat $(PID_FILE)))"; \
	else \
		nohup ./scripts/start.sh > $(LOG_FILE) 2>&1 & echo $$! > $(PID_FILE); \
		echo "Started (pid $$(cat $(PID_FILE))), logs: $(LOG_FILE)"; \
	fi

stop:
	@if [ -f $(PID_FILE) ] && kill -0 "$$(cat $(PID_FILE))" 2>/dev/null; then \
		kill "$$(cat $(PID_FILE))"; \
		while kill -0 "$$(cat $(PID_FILE))" 2>/dev/null; do sleep 0.2; done; \
		echo "Stopped"; \
	else \
		echo "Not running"; \
	fi
	@rm -f $(PID_FILE)

logs:
	@tail -f $(LOG_FILE)

test:
	@cd transcendence && PATH="$(VENV)/bin:$$PATH" ./test.sh

down: stop

clear: stop
	rm -rf $(VENV) $(DATA_DIR)

.PHONY: help setup run start stop logs test build down clear
