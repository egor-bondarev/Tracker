COMPONENT_TESTS_DIR = ./record_service/tests/component
UNIT_TESTS_DIR = ./record_service/tests/unit
ALL_TESTS_DIR = ./record_service/tests

export PYTHONPATH := $(shell pwd)

.PHONY: run_tracker
run_tracker:
	docker-compose up -d --build
	python ./record_service/src/create_db.py

.PHONY: run_tracker_debug
run_tracker_debug:
	docker-compose up --build

.PHONY: stop_tracker
stop_tracker:
	docker-compose down

.PHONY: record_service_component_tests
record_service_component_tests:
	pytest --alluredir allure-results $(COMPONENT_TESTS_DIR)

.PHONY: record_service_unit_tests
record_service_unit_tests:
	pytest --alluredir allure-results $(UNIT_TESTS_DIR)

.PHONY: record_service_all_tests
record_service_all_tests:
	pytest --alluredir allure-results $(ALL_TESTS_DIR)