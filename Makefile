.PHONY: help dev test lint format migrate setup clean

# Default target
help:
	@echo "SortMail Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  dev       Start development environment (Docker)"
	@echo "  test      Run all tests"
	@echo "  lint      Run linters"
	@echo "  format    Format code"
	@echo "  migrate   Run database migrations"
	@echo "  setup     Initial project setup"
	@echo "  clean     Clean up containers and volumes"

# Start development environment
dev:
	docker-compose up -d
	@echo "🚀 Development environment started"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"

# Run tests
test:
	cd backend && pytest -v --cov=app
	cd frontend && npm test

# Run linters
lint:
	cd backend && ruff check . && mypy app --ignore-missing-imports
	cd frontend && npm run lint

# Format code
format:
	cd backend && ruff format . && ruff check --fix .
	cd frontend && npm run format

# Run database migrations
migrate:
	cd backend && alembic upgrade head

# Initial setup
setup:
	cp .env.example .env
	cd backend && python -m venv venv && venv/Scripts/activate && pip install -r requirements-dev.txt
	cd frontend && npm install
	@echo "✅ Setup complete! Edit .env with your API keys."

# Clean up
clean:
	docker-compose down -v
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/.next frontend/node_modules
	@echo "🧹 Cleaned up"
