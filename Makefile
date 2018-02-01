test:
	mypy --ignore-missing-imports postgrespy
	mypy --ignore-missing-imports tests
	PYTHONPATH=. pytest
