all: 

.FORCE:

format: .FORCE
	isort *.py */*.py
	black -l120 .

tests: .FORCE
	pytest -vv tests

coverage: .FORCE
	coverage run -m pytest
	coverage report -m
