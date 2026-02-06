.PHONY: help install run dev migrate migrate-gen migrate-history migrate-rollback build up down stop restart logs shell clean ngrok-url

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Local development (without Docker)
install:  ## Install dependencies with uv
	uv sync

migrate:  ## Run pending database migrations
	uv run alembic upgrade head

migrate-gen:  ## Generate a new migration (usage: make migrate-gen msg="add xyz column")
	uv run alembic revision --autogenerate -m "$(msg)"

migrate-history:  ## Show migration history
	uv run alembic history --verbose

migrate-rollback:  ## Rollback the last migration
	uv run alembic downgrade -1

run:  ## Run the server locally (with migrations)
	uv run alembic upgrade head && uv run uvicorn app.main:api --host 0.0.0.0 --port 3000

dev:  ## Run the server locally with hot reload (with migrations)
	uv run alembic upgrade head && uv run uvicorn app.main:api --host 0.0.0.0 --port 3000 --reload

# Docker commands
build:  ## Build Docker images
	docker compose build

up:  ## Start all services (app + ngrok)
	docker compose up

down:  ## Stop and remove containers
	docker compose down

stop:  ## Stop containers without removing
	docker compose stop

restart:  ## Restart all services
	docker compose restart

logs:  ## View logs (follow mode)
	docker compose logs -f

logs-app:  ## View app logs only
	docker compose logs -f app

shell:  ## Open shell in app container
	docker compose exec app /bin/bash

clean:  ## Remove containers, volumes, and images
	docker compose down -v --rmi local

ngrok-url:  ## Get the ngrok public URL
	@curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null || echo "ngrok not running"
