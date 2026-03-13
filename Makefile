.PHONY: install api dashboard train test lint clean

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

# Lancer les services
api:
	uvicorn app.main:app --reload --port 8000

dashboard:
	streamlit run app/dashboard/app.py --server.port 8501

# ML
train:
	python scripts/train_model.py

# Tests
test:
	pytest tests/ -v --cov=app

# Linting
lint:
	ruff check app/ scripts/ tests/
	black --check app/ scripts/ tests/

format:
	ruff check --fix app/ scripts/ tests/
	black app/ scripts/ tests/

# Nettoyage
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage
