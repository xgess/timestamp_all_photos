.PHONY: clean test

default: test

build-test:
	@pip install --no-cache-dir -r requirements-dev.txt

build:
	@pip install --no-cache-dir -r requirements.txt

clean: ## Remove artifacts
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +
	@rm -f .coverage
	@rm -rf .cache
	@rm -rf test-results

test: build-test clean ## Run tests
	py.test --flakes
