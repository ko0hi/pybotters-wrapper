.PHONY: format lint typecheck test
format:
	poetry run black pybotters_wrapper tests
lint:
	poetry run pflake8 pybotters_wrapper
typecheck:
	poetry run mypy pybotters_wrapper
test:
	poetry run pytest tests

