all: 

.FORCE:

format: .FORCE
	pre-commit

tests: .FORCE
	pytest -vv tests

coverage: .FORCE
	coverage run -m pytest
	coverage report -m
