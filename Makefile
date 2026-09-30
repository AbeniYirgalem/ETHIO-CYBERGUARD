# ETHIO-CYBERGUARD Developer Automation Makefile
.PHONY: install dev test lint security build clean

install:
	python -m pip install --upgrade pip
	pip install -r apps/api/requirements.txt
	pip install pytest pytest-cov
	cd apps/web && npm install

dev:
	@echo "Starting ETHIO-CYBERGUARD local services..."
	python -m uvicorn apps.api.main:app --reload --port 8000 &
	cd apps/web && npm run dev

test:
	python -m pytest tests/ -v

lint:
	python -m compileall apps/ services/ collectors/
	cd apps/web && npx oxlint src/

security:
	python -m pytest tests/security/ -v

build:
	cd apps/web && npm run build
	python -m compileall apps/ services/ collectors/

clean:
	rm -rf .pytest_cache apps/web/dist apps/web/node_modules/.vite
