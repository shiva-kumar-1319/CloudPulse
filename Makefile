.PHONY: help install test run-auth run-order run-inventory run-gateway run-frontend build-frontend clean docker-up docker-down

PYTHON = python
PYTEST = pytest

help:
	@echo "CloudPulse Automation Commands:"
	@echo "  make install        - Install python dependencies across all services"
	@echo "  make test           - Run pytest unit and integration test suite"
	@echo "  make run-auth       - Launch Auth Service (Port 8001)"
	@echo "  make run-order      - Launch Order Service (Port 8002)"
	@echo "  make run-inventory  - Launch Inventory Service (Port 8003)"
	@echo "  make run-gateway    - Launch Unified Control Plane API Gateway (Port 8000)"
	@echo "  make run-frontend   - Start React Frontend dev server (Port 5173)"
	@echo "  make build-frontend - Build React Frontend static production bundle"
	@echo "  make docker-up      - Start local environment via Docker Compose"
	@echo "  make docker-down    - Stop local Docker Compose environment"
	@echo "  make clean          - Clean temporary database files and caches"

install:
	$(PYTHON) -m pip install -r services/auth_service/requirements.txt
	$(PYTHON) -m pip install -r services/order_service/requirements.txt
	$(PYTHON) -m pip install -r services/inventory_service/requirements.txt
	$(PYTHON) -m pip install -r services/api_gateway/requirements.txt

test:
	PYTHONPATH=. $(PYTEST) -v tests/

run-auth:
	PYTHONPATH=. $(PYTHON) -m services.auth_service.app.main

run-order:
	PYTHONPATH=. $(PYTHON) -m services.order_service.app.main

run-inventory:
	PYTHONPATH=. $(PYTHON) -m services.inventory_service.app.main

run-gateway:
	PYTHONPATH=. $(PYTHON) -m services.api_gateway.app.main

run-frontend:
	cd frontend && npm install && npm run dev

build-frontend:
	cd frontend && npm install && npm run build

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
