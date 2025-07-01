# Discord Emoji Bot

A Discord bot that generates custom emojis using OpenAI's DALL-E API and adds them as reactions to messages. Perfect for creating quick, contextual emoji reactions in your Discord server.

## Features

- 🎨 **AI-Generated Emojis**: Uses OpenAI DALL-E 3 to create custom emojis.
- 🖱️ **Context Menu Integration**: Right-click any message to generate an emoji reaction.
- 🔄 **Automatic Cleanup**: Emojis are automatically deleted after use to save server space.
- 🐳 **Docker Ready**: Fully containerized for easy deployment.
- 🔒 **Secure**: Runs as non-root user in container.
- 🚀 **CI/CD Ready**: Includes Woodpecker CI pipelines for automated testing and deployment.

## Table of Contents

- [Discord Emoji Bot](#discord-emoji-bot)
  - [Features](#features)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Bot Permissions](#bot-permissions)
  - [Quick Start with Docker](#quick-start-with-docker)
  - [Local Development Setup](#local-development-setup)
    - [Why Use a Virtual Environment?](#why-use-a-virtual-environment)
    - [Automated Setup (Recommended)](#automated-setup-recommended)
    - [Manual Setup](#manual-setup)
    - [IDE Integration](#ide-integration)
  - [Usage](#usage)
  - [Development Commands (Makefile)](#development-commands-makefile)
  - [CI/CD Pipeline (Woodpecker CI)](#cicd-pipeline-woodpecker-ci)
    - [Pipeline Overview](#pipeline-overview)
    - [Pipeline Files](#pipeline-files)
    - [Pipeline Stages](#pipeline-stages)
    - [Secrets Setup](#secrets-setup)
  - [Deployment](#deployment)
    - [Deploying on an OCI Instance (or other VM)](#deploying-on-an-oci-instance-or-other-vm)
    - [Automatic vs. Manual Deployment](#automatic-vs-manual-deployment)
  - [Troubleshooting](#troubleshooting)
    - [Common Bot Issues](#common-bot-issues)
    - [Pipeline \& CI Issues](#pipeline--ci-issues)
  - [Security Notes](#security-notes)
  - [Contributing](#contributing)
  - [License](#license)

## Prerequisites

- **Discord Bot Token**: Get one from the [Discord Developer Portal](https://discord.com/developers/applications).
- **OpenAI API Key**: Get one from the [OpenAI Platform](https://platform.openai.com/api-keys).
- **Docker and Docker Compose**: Required for containerized deployment.

## Bot Permissions

Your Discord bot needs the following permissions on your server:
- `Use Slash Commands`
- `Manage Emojis and Stickers`
- `Add Reactions`
- `Read Message History`

## Quick Start with Docker

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd emoji_gen_bot
    ```

2.  **Set up environment variables**:
    Create a `.env` file in the root directory and add your tokens. You can copy the example file:
    ```bash
    cp .env.example .env
    # Now, edit the .env file with your actual tokens
    ```

3.  **Build and run with Docker Compose**:
    ```bash
    docker-compose up --build -d
    ```

4.  **Check logs**:
    ```bash
    docker-compose logs -f
    ```

## Local Development Setup

For local development, a Python virtual environment is recommended to isolate dependencies.

### Why Use a Virtual Environment?
- **Isolated dependencies**: Avoids conflicts with global Python packages.
- **Reproducible builds**: Ensures consistent package versions.
- **Clean development**: Easy to reset and recreate the environment.

### Automated Setup (Recommended)
The included script sets up the virtual environment and installs all dependencies.

```bash
# Run the setup script
./scripts/setup-venv.sh

# Activate the virtual environment
source venv/bin/activate
```

### Manual Setup
```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt
```

### IDE Integration
- **VS Code**: Open the Command Palette (`Cmd+Shift+P`), select "Python: Select Interpreter", and choose `./venv/bin/python`.
- **PyCharm**: Go to `Settings > Project > Python Interpreter`, click the gear icon, select "Add", choose "Existing environment", and point to `./venv/bin/python`.


## Usage

1.  **Invite the bot** to your Discord server with the required [permissions](#bot-permissions).
2.  **Right-click any message** in your server.
3.  Select **"Generate Emoji Reaction"** from the context menu.
4.  **Fill in the modal**:
    - **Emoji Name**: A short name for the emoji (e.g., "happycat").
    - **Prompt**: A description of the emoji you want to generate.
5.  **Submit** and wait for the bot to generate and react with your custom emoji!

## Development Commands (Makefile)

Use the `Makefile` for common development tasks. These commands automatically handle the virtual environment if it exists.

| Command | Description |
|---|---|
| `make setup` | Sets up the development environment. |
| `make ci-test` | Runs the full suite of tests and linters. |
| `make ci-build`| Builds and tests the Docker image. |
| `make format` | Formats code with Black and isort. |
| `make security`| Runs security scans with bandit and safety. |
| `make venv-dev` | Runs the bot locally in the virtual environment. |
| `make venv-clean`| Removes the virtual environment. |


## CI/CD Pipeline (Woodpecker CI)

This project uses a comprehensive Woodpecker CI pipeline for automation.

### Pipeline Overview
- ✅ **Code Quality**: Runs linting, formatting, and security scans.
- 🏗️ **Build**: Creates and tests Docker images.
- 🚀 **Deploy**: Handles automated production deployments.
- 📦 **Package**: Creates deployment artifacts.

### Pipeline Files
- `.woodpecker.yml`: The main pipeline configuration.
- `.woodpecker/`: Directory for additional pipeline definitions (e.g., `test.yml`, `deploy.yml`).

### Pipeline Stages
1.  **Lint**: Code formatting and style checks.
2.  **Security Scan**: Vulnerability and static security analysis.
3.  **Build**: Docker image creation.
4.  **Test Container**: Validation of Docker container functionality.
5.  **Package**: Creation of deployment artifacts.
6.  **Deploy**: Production deployment (triggers on `main` branch only).
7.  **Notify**: Pipeline status notifications.

### Secrets Setup
Configure these secrets in your Woodpecker CI repository settings:

| Secret Name | Description | Required |
|---|---|---|
| `DISCORD_BOT_TOKEN` | Your Discord bot token. | Yes |
| `OPENAI_API_KEY` | Your OpenAI API key. | Yes |
| `GUILD_ID` | Discord server ID for faster testing. | No |
| `RESPONSE_CHANNEL`| Channel for bot responses. | No |

## Deployment

### Deploying on an OCI Instance (or other VM)

1.  **Install Docker on your instance**:
    ```bash
    sudo apt update
    sudo apt install docker.io docker-compose -y
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    # Log out and log back in for the group change to take effect
    ```

2.  **Clone the repository and configure the environment**:
    ```bash
    git clone <your-repo-url>
    cd emoji_gen_bot
    cp .env.example .env
    nano .env  # Add your tokens
    ```

3.  **Deploy with Docker Compose**:
    ```bash
    docker-compose up --build -d
    ```

### Automatic vs. Manual Deployment
- **Automatic**: Deployments are triggered automatically by a push to the `main` branch if the pipeline succeeds.
- **Manual**: You can manually trigger a deployment from the Woodpecker CI dashboard.

## Troubleshooting

### Common Bot Issues
- **"I don't have permission to add emojis"**: Ensure the bot has the "Manage Emojis and Stickers" permission and that the server hasn't reached its emoji limit.
- **Commands not appearing**: Set the `GUILD_ID` environment variable for faster command syncing during development. Otherwise, global commands can take up to an hour to sync.
- **Container not starting**: Check the logs with `docker-compose logs -f` and verify that all required environment variables are set correctly in your `.env` file.

### Pipeline & CI Issues
- **Pipeline Won't Start**: Check your `.woodpecker.yml` syntax and ensure the repository is correctly connected to Woodpecker CI.
- **Build Failures**: Review pipeline logs for errors. Test Docker builds locally with `make ci-build` before pushing.
- **Secret Access Errors**: Verify that all required secrets are configured correctly in your Woodpecker CI repository settings.

## Security Notes

- **Never commit your `.env` file** or any other files containing sensitive tokens.
- The container is configured to run as a non-root user for enhanced security.
- For production, consider using a more robust secrets management solution like Docker secrets or a cloud provider's secret manager.

## Contributing

1.  Fork the repository.
2.  Create a new feature branch.
3.  Make your changes and test them thoroughly.
4.  Submit a pull request. The CI pipeline will automatically validate your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
