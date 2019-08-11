SRC_DIRS = libsalesforce

##@ bootup

.PHONY: install
install: ## Installs missing dependencies with flit
install: flit-install pyenv-rehash

flit-install:
	flit install

pyenv-rehash:
	# as we don't use flit, we have to manually rehash the environment.
	command -v pyenv && pyenv rehash

##@ Code Checks

.PHONY: test
test: ## Runs all the tests
test:
	python -m pytest tests

.PHONY: fixlint autofix
fixlint: autofix
autofix: ## Attempts to rectify any linting issues
autofix:
	autoflake --in-place --remove-unused-variables --recursive $(SRC_DIRS)
	isort --recursive $(SRC_DIRS)
	black $(SRC_DIRS)

.PHONY: lint
lint: ## Checks the code for any style violations
lint:
	autoflake --check --remove-unused-variables --recursive $(SRC_DIRS)
	isort --check-only --recursive $(SRC_DIRS)
	black --check $(SRC_DIRS)
	mypy $(SRC_DIRS)
