.PHONY: clean test

default: test

build-test:
	@pipenv install --dev

build:
	@pipenv install

clean: ## Remove artifacts
	@find . -name "*.pyc" -delete
	@find . -name "*.pytest_cache" -delete
	@find . -name "*.pyo" -delete
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +
	@rm -f .coverage
	@rm -rf .cache
	@rm -rf test-results

test: build-test clean ## Run tests
	py.test --flakes
