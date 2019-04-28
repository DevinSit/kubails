.DEFAULT_GOAL := show-help
.PHONY: show-help install install-dev install-deps install-deps-all test type-check lint test-all test-watch lint-watch test-all-watch

###############################################################################
# GLOBALS
###############################################################################

SOURCE_FOLDER = kubails

###############################################################################
# COMMANDS
###############################################################################

## Install the apps for regular use (non-development)
install:
	sudo pip3 install .

## Upgrade the apps for regular use
upgrade:
	sudo pip3 install --upgrade .

## Install the apps for development use (editing files automatically updates installed versions)
install-dev:
	sudo pip3 install --editable .

## Installs just the app dependencies into a Pipenv (virtualenv) environment
install-deps:
	pipenv install

## Installs all of the dependencies into a Pipenv (virtualenv) environment
install-deps-all:
	pipenv install --dev

## Runs the whole test suite
test:
	PYTHONPATH=./$(SOURCE_FOLDER) pipenv run python3 -m pytest $(SOURCE_FOLDER)

## Runs the whole test suite and produces a command line coverage report
test-cov:
	PYTHONPATH=./$(SOURCE_FOLDER) pipenv run python3 -m pytest --cov-config=setup.cfg --cov=$(SOURCE_FOLDER) $(SOURCE_FOLDER)

## Runs the whole test suite and produces an HTML coverage report
test-cov-html:
	PYTHONPATH=./$(SOURCE_FOLDER) pipenv run python3 -m pytest --cov-config=setup.cfg --cov=$(SOURCE_FOLDER) --cov-report=html $(SOURCE_FOLDER)

## Runs the static type checker
type-check:
	MYPYPATH="$$(pwd)/$(SOURCE_FOLDER)" pipenv run python3 -m mypy $(SOURCE_FOLDER)

## Runs the flake8 linter and static type checker
lint: type-check
	pipenv run python3 -m flake8 $(SOURCE_FOLDER)

## Runs the linter and the test suite
test-all: lint test

ci: lint test-cov

## Runs the test suite whenever a Python file changes
test-watch:
	find . -name '*.py' | entr make test

## Runs the linter whenever a Python file changes
lint-watch:
	find . -name '*.py' | entr make lint

## Runs the linter and the test suite whenever a Python file changes
test-all-watch:
	find . -name '*.py' | entr make test-all

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
show-help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
