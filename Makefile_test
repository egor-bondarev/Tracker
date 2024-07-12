
COMPONENT_TESTS_DIR = ./sampleService/tests/component
UNIT_TESTS_DIR = ./sampleService/tests/unit
ALL_TESTS_DIR = ./sampleService/tests
LOAD_TESTS_DIR = ./sampleService/tests/load
export PYTHONPATH := $(shell pwd)/sampleService
export HOST := 0.0.0.0
export PORT := 8000

.PHONY: sample_component_tests
sample_component_tests:
	pytest --alluredir allure-results $(COMPONENT_TESTS_DIR)

.PHONY: sample_unit_tests
sample_unit_tests:
	pytest --alluredir allure-results $(UNIT_TESTS_DIR)

.PHONY: sample_all_tests
sample_all_tests:
	pytest --alluredir allure-results $(ALL_TESTS_DIR)

.PHONY: run_load_test_post_user
run_load_test_post_user:
	K6_WEB_DASHBOARD_EXPORT=report.html K6_WEB_DASHBOARD=true K6_WEB_DASHBOARD_OPEN=true k6 run --vus ${USERS_COUNT} --duration ${DURATION} $(LOAD_TESTS_DIR)/post-users.js

.PHONY: run_load_test_get_one_user
run_load_test_get_one_user:
	K6_WEB_DASHBOARD_EXPORT=report.html K6_WEB_DASHBOARD=true K6_WEB_DASHBOARD_OPEN=true k6 run --vus ${USERS_COUNT} --duration ${DURATION} $(LOAD_TESTS_DIR)/get-one-user.js

.PHONY: sample_run_dev
sample_run_dev:
	docker-compose -f ./sampleService/docker-compose.testing.yml --env-file=./sampleService/.env.testing up -d --build
	python ./sampleService/src/create_sample_db.py

.PHONY: sample_stop_dev
sample_stop_dev:
	docker-compose -f ./sampleService/docker-compose.testing.yml --env-file=./sampleService/.env.testing down

.PHONY: sample_print_vars
sample_print_vars: 
	echo $(PYTHONPATH)
	echo $(POSTGRESQL_PASSWORD)

.PHONY: test
test:
	echo "${BAR}"