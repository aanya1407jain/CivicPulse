.PHONY: install test test-fast lint format typecheck coverage clean run help

# ── Variables ──────────────────────────────────────────────────────────────────
PYTHON   := python3
PIP      := pip3
APP      := app.py
SRC_DIRS := app.py services/ components/ regions/ config/ utils/ views/

help:
	@echo "CivicPulse — Developer Commands"
	@echo "================================"
	@echo "  make install    Install all dependencies"
	@echo "  make run        Start the Streamlit app"
	@echo "  make test       Run full test suite with coverage"
	@echo "  make test-fast  Run tests (no coverage — faster)"
	@echo "  make lint       Run ruff linter"
	@echo "  make format     Auto-fix formatting with ruff"
	@echo "  make typecheck  Run mypy type checker"
	@echo "  make coverage   Open HTML coverage report"
	@echo "  make clean      Remove cache and build artifacts"

install:
	$(PIP) install -r requirements.txt --break-system-packages

run:
	streamlit run $(APP)

test:
	$(PYTHON) -m pytest \
		--tb=short \
		--cov=. \
		--cov-report=term-missing \
		--cov-report=html:htmlcov \
		--cov-fail-under=80 \
		--cov-omit="tests/*,*/__init__.py,.streamlit/*" \
		-v

test-fast:
	$(PYTHON) -m pytest --tb=short -v -m "not integration and not slow"

test-integration:
	$(PYTHON) -m pytest --tb=short -v -m "integration"

lint:
	$(PYTHON) -m ruff check $(SRC_DIRS)

format:
	$(PYTHON) -m ruff check --fix $(SRC_DIRS)
	$(PYTHON) -m ruff format $(SRC_DIRS)

typecheck:
	$(PYTHON) -m mypy $(SRC_DIRS) --ignore-missing-imports

coverage:
	$(PYTHON) -m pytest \
		--cov=. \
		--cov-report=html:htmlcov \
		--cov-omit="tests/*,*/__init__.py"
	@echo "Coverage report: htmlcov/index.html"
	@$(PYTHON) -m webbrowser htmlcov/index.html 2>/dev/null || true

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage 2>/dev/null || true
	@echo "Cleaned."
