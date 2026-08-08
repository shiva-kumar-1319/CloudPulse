.PHONY: help install test run-auth run-order run-inventory clean docker-up docker-down

PYTHON = python
PYTEST = pytest

help:
	@echo "CloudPulse Automation Commands:"
	@echo "  make install        - Install python dependencies across all services"
	@echo "  make test           - Run pytest unit and integration test suite"
	@echo "  make run-auth       - Launch Auth Service (Port 8001)"
	@echo "  make run-order      - Launch Order Service (Port 8002)"
	@echo "  make run-inventory  - Launch Inventory Service (Port 8003)"
	@echo "  make docker-up      - Start local environment via Docker Compose"
	@echo "  make docker-down    - Stop local Docker Compose environment"
	@echo "  make clean          - Clean temporary database files and caches"

install:
	$(PYTHON) -m pip install -r services/auth-service/requirements.txt
	$(PYTHON) -m pip install -r services/order-service/requirements.txt
	$(PYTHON) -m pip install -r services/inventory-service/requirements.txt

test:
	PYTHONPATH=. $(PYTEST) -v tests/

run-auth:
	PYTHONPATH=. $(PYTHON) -m services.auth_service.app.main

run-order:
	PYTHONPATH=. $(PYTHON) -m services.order_service.app.main

run-inventory:
	PYTHONPATH=. $(PYTHON) -m services.inventory_service.app.main

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.db" -delete
	find . -type f -name "*.sqlite" -delete
	rm -rf .pytest_cache
