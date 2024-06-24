#.PHONY: component_tests unit_tests all_tests run_dev stop_dev

COMPONENT_TESTS_DIR = ./sampleService/tests/component
UNIT_TESTS_DIR = ./sampleService/tests/unit
ALL_TESTS_DIR = ./sampleService/tests
export PYTHONPATH := $(shell pwd)/sampleService

.PHONY: sample_component_tests
sample_component_tests:
	ls
	ls ./sampleService
	echo "$(PWD)"
	pytest /home/runner/work/Tracker/Tracker/sampleService/tests/component

.PHONY: sample_unit_tests
sample_unit_tests:
	pytest $(UNIT_TESTS_DIR)

.PHONY: sample_all_tests
sample_all_tests:
	pytest $(ALL_TESTS_DIR)

.PHONY: sample_run_dev
sample_run_dev:
	docker-compose -f ./sampleService/docker-compose.testing.yml --env-file=./sampleService/.env.testing up --build

.PHONY: sample_stop_dev
sample_stop_dev:
	docker-compose -f ./sampleService/docker-compose.testing.yml --env-file=./sampleService/.env.testing down

.PHONY: sample_print_vars
sample_print_vars: 
	echo $(PYTHONPATH)