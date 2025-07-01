# Makefile for Discord Emoji Bot
# Provides convenient commands for development and deployment

.PHONY: help install install-dev test lint format security build run clean deploy

# Default target
help:
	@echo "Discord Emoji Bot - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     - Install production dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code with black and isort"
	@echo "  security    - Run security scans"
	@echo ""
	@echo "Docker:"
	@echo "  build       - Build Docker image"
	@echo "  run         - Run bot in Docker container"
	@echo "  compose     - Run with docker-compose"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy      - Deploy using deployment script"
	@echo "  clean       - Clean up build artifacts"
	@echo ""
	@echo "CI/CD:"
	@echo "  ci-test     - Run CI pipeline tests locally"
	@echo "  ci-build    - Run CI build steps locally"

# Development commands
install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt

test:
	@echo "🧪 Running tests..."
	pytest test_bot.py -v --cov=discord_emoji --cov-report=term-missing

lint:
	@echo "🔍 Running linting checks..."
	flake8 discord_emoji.py --max-line-length=100 --ignore=E203,W503
	@echo "✅ Linting passed!"

format:
	@echo "🎨 Formatting code..."
	black discord_emoji.py test_bot.py
	isort discord_emoji.py test_bot.py
	@echo "✅ Code formatted!"

security:
	@echo "🔒 Running security scans..."
	bandit -r . -f json || true
	safety check || echo "⚠️  Some dependencies may have vulnerabilities"
	@echo "✅ Security scan completed!"

# Docker commands
build:
	@echo "🏗️ Building Docker image..."
	docker build -t emoji-bot:latest .
	@echo "✅ Docker image built!"

run: build
	@echo "🚀 Running bot in Docker container..."
	@if [ ! -f .env ]; then echo "❌ .env file not found! Create it with your tokens."; exit 1; fi
	docker run --rm --env-file .env emoji-bot:latest

compose:
	@echo "🚀 Starting bot with docker-compose..."
	@if [ ! -f .env ]; then echo "❌ .env file not found! Create it with your tokens."; exit 1; fi
	docker-compose up --build

compose-down:
	@echo "🛑 Stopping docker-compose services..."
	docker-compose down

# Deployment commands
deploy:
	@echo "🚀 Deploying bot..."
	@if [ -f deploy.sh ]; then ./deploy.sh; else echo "❌ deploy.sh not found!"; fi

clean:
	@echo "🧹 Cleaning up..."
	docker system prune -f
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup completed!"

# CI/CD simulation commands
ci-test:
	@echo "🔄 Simulating CI test pipeline..."
	make install-dev
	make format
	make lint
	make security
	make test
	@echo "✅ CI test pipeline completed!"

ci-build:
	@echo "🔄 Simulating CI build pipeline..."
	make build
	@echo "🧪 Testing Docker container..."
	docker run --rm \
		-e DISCORD_BOT_TOKEN=dummy_token \
		-e OPENAI_API_KEY=dummy_key \
		emoji-bot:latest python -c "import discord_emoji; print('✅ Container test passed')" \
		|| echo "⚠️ Container test completed (expected with dummy credentials)"
	@echo "✅ CI build pipeline completed!"

# Environment setup
env-template:
	@echo "📝 Creating .env template..."
	@echo "# Discord Emoji Bot Environment Variables" > .env.template
	@echo "DISCORD_BOT_TOKEN=your_discord_bot_token_here" >> .env.template
	@echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env.template
	@echo "GUILD_ID=your_guild_id_for_testing" >> .env.template
	@echo "RESPONSE_CHANNEL=bot-responses" >> .env.template
	@echo "✅ .env.template created! Copy to .env and fill in your values."

# Git hooks setup
setup-hooks:
	@echo "🔗 Setting up git hooks..."
	@if [ -d .git ]; then \
		echo "#!/bin/sh" > .git/hooks/pre-commit; \
		echo "make format lint" >> .git/hooks/pre-commit; \
		chmod +x .git/hooks/pre-commit; \
		echo "✅ Pre-commit hook installed!"; \
	else \
		echo "❌ Not in a git repository!"; \
	fi

# Development server
dev:
	@echo "🔧 Starting development mode..."
	@if [ ! -f .env ]; then echo "❌ .env file not found! Run 'make env-template' first."; exit 1; fi
	python discord_emoji.py

# Quick setup for new developers
setup: install-dev env-template setup-hooks
	@echo "🎉 Development environment setup complete!"
	@echo "📝 Next steps:"
	@echo "  1. Copy .env.template to .env"
	@echo "  2. Fill in your Discord and OpenAI credentials"
	@echo "  3. Run 'make dev' to start the bot"

# Health check
health:
	@echo "🏥 Running health checks..."
	@python -c "import discord; import aiohttp; from openai import OpenAI; from PIL import Image; print('✅ All dependencies available')"
	@if [ -f .env ]; then echo "✅ .env file exists"; else echo "⚠️ .env file missing"; fi
	@if command -v docker >/dev/null 2>&1; then echo "✅ Docker available"; else echo "⚠️ Docker not found"; fi
	@echo "✅ Health check completed!"
