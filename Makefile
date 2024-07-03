export PYTHONPATH := $(shell pwd)

.PHONY: run_tracker
run_tracker:
	docker-compose up -d --build
	python ./record_service/src/create_db.py

.PHONY: run_tracker_debug
run_tracker:
	docker-compose up --build

.PHONY: stop_tracker
stop_tracker:
	docker-compose down