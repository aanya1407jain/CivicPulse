.PHONY: test lint type-check coverage run clean

test:
	python -m pytest tests/ -v --tb=short

integration:
	python -m pytest tests/test_integration.py -v -m integration

coverage:
	python -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html --cov-fail-under=80

lint:
	python -m ruff check . --fix

type-check:
	python -m mypy . --ignore-missing-imports

run:
	streamlit run app.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -name "*.pyc" -delete; \
	rm -rf .coverage htmlcov/ .mypy_cache/ .ruff_cache/
