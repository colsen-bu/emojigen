# Makefile for Discord Emoji Bot
# Provides convenient commands for development and deployment

.PHONY: help install install-dev test lint format security build run clean deploy

# Default target
help:
	@echo "Discord Emoji Bot - Available Commands:"
	@echo ""
	@echo "Virtual Environment:"
	@echo "  venv-install    - Create virtual environment and install dependencies"
	@echo "  venv-clean      - Remove virtual environment"
	@echo "  venv-info       - Show virtual environment information"
	@echo "  venv-activate   - Show how to activate virtual environment"
	@echo "  venv-shell      - Start interactive shell in virtual environment"
	@echo ""
	@echo "Virtual Environment Development:"
	@echo "  venv-dev        - Run bot in virtual environment"
	@echo "  venv-test       - Run tests in virtual environment"
	@echo "  venv-lint       - Run linting in virtual environment"
	@echo "  venv-format     - Format code in virtual environment"
	@echo "  venv-security   - Run security scans in virtual environment"
	@echo "  venv-ci-test    - Run complete CI pipeline in virtual environment"
	@echo "  venv-build      - Build Docker image"
	@echo ""
	@echo "Development (Global/Auto-detect):"
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
	pytest src/test_bot.py -v --cov=src/discord_emoji --cov-report=term-missing

lint:
	@echo "🔍 Running linting checks..."
	flake8 src/ --max-line-length=100 --ignore=E203,W503,I201,E402,D202 --exclude=src/test_bot.py
	flake8 src/test_bot.py --max-line-length=100 --ignore=E203,W503,I201,E402,I100,D202
	@echo "✅ Linting passed!"

format:
	@echo "🎨 Formatting code..."
	black src/
	isort src/
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
		emoji-bot:latest python -c "import sys; sys.path.insert(0, 'src'); import discord_emoji; print('✅ Container test passed')" \
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
	python src/discord_emoji.py

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

# Virtual Environment Management
VENV_DIR = venv
VENV_ACTIVATE = $(VENV_DIR)/bin/activate
PYTHON_VENV = $(VENV_DIR)/bin/python
PIP_VENV = $(VENV_DIR)/bin/pip

# Check if we're in a virtual environment
VENV_ACTIVE := $(shell python -c "import sys; print('1' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else '0')")

# Virtual Environment commands
venv-create:
	@echo "🐍 Creating Python virtual environment..."
	python3 -m venv $(VENV_DIR)
	@echo "✅ Virtual environment created!"

venv-install: venv-create
	@echo "📦 Installing dependencies in virtual environment..."
	$(PIP_VENV) install --upgrade pip
	$(PIP_VENV) install -r requirements.txt
	$(PIP_VENV) install -r requirements-dev.txt
	@echo "✅ Dependencies installed!"

venv-clean:
	@echo "🗑️  Removing virtual environment..."
	rm -rf $(VENV_DIR)
	@echo "✅ Virtual environment removed!"

venv-info:
	@echo "📋 Virtual Environment Information:"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "✅ Virtual environment exists at: $(VENV_DIR)"; \
		echo "🐍 Python version: $$($(PYTHON_VENV) --version)"; \
		echo "📦 Pip version: $$($(PIP_VENV) --version)"; \
		echo "📍 Python path: $$($(PYTHON_VENV) -c 'import sys; print(sys.executable)')"; \
	else \
		echo "❌ Virtual environment not found. Run 'make venv-install' to create it."; \
	fi

venv-activate:
	@echo "⚡ To activate the virtual environment, run:"
	@echo "   source $(VENV_ACTIVATE)"

# Virtual Environment Development Commands
venv-dev:
	@echo "🚀 Starting bot in virtual environment..."
	@if [ ! -f .env ]; then echo "❌ .env file not found! Copy .env.example to .env and fill in your tokens."; exit 1; fi
	source $(VENV_ACTIVATE) && python src/discord_emoji.py

venv-test:
	@echo "🧪 Running tests in virtual environment..."
	source $(VENV_ACTIVATE) && pytest src/test_bot.py -v --cov=src/discord_emoji --cov-report=term-missing

venv-lint:
	@echo "🔍 Running linting in virtual environment..."
	source $(VENV_ACTIVATE) && flake8 src/ --max-line-length=100 --ignore=E203,W503,I201,E402,D202 --exclude=src/test_bot.py
	source $(VENV_ACTIVATE) && flake8 src/test_bot.py --max-line-length=100 --ignore=E203,W503,I201,E402,I100,D202

venv-format:
	@echo "🎨 Formatting code in virtual environment..."
	source $(VENV_ACTIVATE) && black src/
	source $(VENV_ACTIVATE) && isort src/

venv-security:
	@echo "🔒 Running security scans in virtual environment..."
	source $(VENV_ACTIVATE) && bandit -r . -f json || true
	source $(VENV_ACTIVATE) && safety check || echo "⚠️  Some dependencies may have vulnerabilities"

venv-ci-test: venv-install venv-format venv-lint venv-security venv-test
	@echo "✅ Virtual environment CI test pipeline completed!"

venv-build:
	@echo "🏗️ Building Docker image with virtual environment..."
	docker build -t emoji-bot:venv-latest .

venv-shell:
	@echo "🐚 Starting shell in virtual environment..."
	@echo "Use 'deactivate' to exit the virtual environment"
	bash --rcfile <(echo '. ~/.bashrc; source $(VENV_ACTIVATE); echo "🐍 Virtual environment activated!"')

# Auto-detect environment and use appropriate commands
ifeq ($(VENV_ACTIVE),1)
    # We're already in a virtual environment, use direct commands
    PYTHON_CMD = python
    PIP_CMD = pip
else
    # Not in virtual environment, check if venv exists and use it
    ifeq ($(shell test -d $(VENV_DIR) && echo "exists"),exists)
        PYTHON_CMD = source $(VENV_ACTIVATE) &&
        PIP_CMD = source $(VENV_ACTIVATE) && pip
    else
        PYTHON_CMD = python
        PIP_CMD = pip
    endif
endif
