.PHONY: up down logs build restart compile-requirements-backend compile-requirements-frontend

COMPOSE=docker-compose

up: compile-requirements-backend compile-requirements-frontend
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

logs-backend:
	$(COMPOSE) logs -f backend

logs-frontend:
	$(COMPOSE) logs -f frontend

compile-requirements-backend:
	pip-compile pyproject.toml -o src/qualpipe_webapp/backend/requirements.txt
	pip-compile pyproject.toml --extra webdev -o src/qualpipe_webapp/backend/requirements-dev.txt

compile-requirements-frontend:
	pip-compile pyproject.toml --extra frontend -o src/qualpipe_webapp/frontend/requirements.txt
	pip-compile pyproject.toml --extra frontend --extra webdev -o src/qualpipe_webapp/frontend/requirements-dev.txt

build: compile-requirements-backend compile-requirements-frontend
	$(COMPOSE) build

build-dev: compile-requirements-backend compile-requirements-frontend
	$(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml build

up-dev: compile-requirements-backend compile-requirements-frontend
	$(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up

restart:
	$(COMPOSE) down && $(COMPOSE) up --build -d

prune:
	docker system prune -f
