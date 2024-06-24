#.PHONY: component_tests unit_tests all_tests run_dev stop_dev

COMPONENT_TESTS_DIR = ./tests/component/
UNIT_TESTS_DIR = ./tests/unit
ALL_TESTS_DIR = ./tests
export PYTHONPATH := $(shell pwd)

.PHONY: component_tests
component_tests:
	pytest $(COMPONENT_TESTS_DIR)

.PHONY: unit_tests
unit_tests:
	pytest $(UNIT_TESTS_DIR)

.PHONY: all_tests
all_tests:
	pytest $(ALL_TESTS_DIR)

.PHONY: run_dev
run_dev:
	docker-compose -f docker-compose.testing.yml --env-file=.env.testing up --build

.PHONY: stop_dev
stop_dev:
	docker-compose -f docker-compose.testing.yml --env-file=.env.testing down

.PHONY: print_vars
print_vars: 
	echo $(PYTHONPATH)