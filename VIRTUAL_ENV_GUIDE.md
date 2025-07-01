# Virtual Environment Development Guide

This guide explains how to set up and use a Python virtual environment for developing the Discord Emoji Bot.

## 🐍 Why Use a Virtual Environment?

Virtual environments provide:
- **Isolated dependencies** - No conflicts with global Python packages
- **Reproducible builds** - Consistent package versions across different machines
- **Clean development** - Easy to reset and recreate the environment
- **Project-specific packages** - Different projects can use different package versions

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Run the setup script
./setup-venv.sh

# Activate the virtual environment
source venv/bin/activate
```

### Option 2: Manual Setup
```bash
# Create virtual environment
make venv-install

# Activate virtual environment
source venv/bin/activate
```

### Option 3: Use Makefile Commands (No activation needed)
```bash
# All commands automatically use virtual environment if it exists
make venv-dev        # Run the bot
make venv-test       # Run tests
make venv-lint       # Run linting
```

## 📋 Available Commands

### Environment Management
```bash
make venv-install    # Create venv and install all dependencies
make venv-clean      # Remove virtual environment
make venv-info       # Show virtual environment details
make venv-activate   # Show activation command
make venv-shell      # Start interactive shell in venv
```

### Development Commands
```bash
make venv-dev        # Run the Discord bot
make venv-test       # Run pytest tests
make venv-lint       # Run flake8 linting
make venv-format     # Format code with black/isort
make venv-security   # Run security scans
make venv-ci-test    # Run complete CI pipeline
```

## 🔄 Daily Development Workflow

### Starting Development
```bash
# Option 1: Use Makefile (auto-handles venv)
make venv-dev

# Option 2: Manual activation
source venv/bin/activate
python discord_emoji.py
```

### Running Tests
```bash
# Option 1: Using Makefile
make venv-test

# Option 2: Manual
source venv/bin/activate
pytest test_bot.py -v
```

### Code Quality Checks
```bash
# Format code
make venv-format

# Run linting
make venv-lint

# Complete quality check
make venv-ci-test
```

## 🎯 Environment Status

Check if you're in a virtual environment:
```bash
# Show current environment info
make venv-info

# Check if virtual environment is active
echo $VIRTUAL_ENV
```

## 🔧 Package Management

### Installing New Packages
```bash
# Activate virtual environment first
source venv/bin/activate

# Install package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Updating Dependencies
```bash
# Update all packages
source venv/bin/activate
pip install --upgrade -r requirements.txt -r requirements-dev.txt

# Or recreate environment
make venv-clean
make venv-install
```

## 🐳 Docker Integration

The virtual environment works alongside Docker:
```bash
# Build Docker image (uses requirements.txt)
make venv-build

# Run in Docker (production-like environment)
make compose

# Development in virtual environment
make venv-dev
```

## 📁 Directory Structure

```
emoji_gen_bot/
├── venv/                    # Virtual environment (ignored by git)
│   ├── bin/                 # Executables (python, pip, etc.)
│   ├── lib/                 # Installed packages
│   └── pyvenv.cfg          # Virtual environment config
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── setup-venv.sh           # Automated setup script
└── Makefile                # Development commands
```

## 🛠️ Troubleshooting

### Virtual Environment Not Working
```bash
# Check Python version
python3 --version

# Recreate virtual environment
make venv-clean
make venv-install

# Verify installation
make venv-info
```

### Package Installation Issues
```bash
# Update pip
source venv/bin/activate
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Check installed packages
pip list

# Verify package is installed
pip show package-name
```

## 🎪 IDE Integration

### VS Code
1. Open Command Palette (`Cmd+Shift+P`)
2. Select "Python: Select Interpreter"
3. Choose `./venv/bin/python`

### PyCharm
1. Go to Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Existing environment"
4. Choose `./venv/bin/python`

## 🔄 CI/CD Integration

The virtual environment setup is integrated with CI/CD:

```yaml
# Woodpecker CI automatically handles virtual environments
# Local testing matches CI environment
make venv-ci-test
```

## 📝 Best Practices

1. **Always activate** the virtual environment before development
2. **Use Makefile commands** for consistency
3. **Update requirements.txt** when adding packages
4. **Test in clean environment** regularly:
   ```bash
   make venv-clean
   make venv-install
   make venv-test
   ```
5. **Don't commit** the `venv/` directory
6. **Document** any new dependencies in comments

## 🆘 Getting Help

```bash
# Show all available commands
make help

# Get virtual environment info
make venv-info

# Check environment status
make health
```
