# Discord Emoji Bot

A Discord bot that generates custom emojis using OpenAI's DALL-E API and adds them as reactions to messages. Perfect for creating quick, contextual emoji reactions in your Discord server.

## Features

- 🎨 **AI-Generated Emojis**: Uses OpenAI DALL-E 3 to create custom emojis
- 🖱️ **Context Menu Integration**: Right-click any message to generate an emoji reaction
- 🔄 **Automatic Cleanup**: Emojis are automatically deleted after use to save server space
- 🐳 **Docker Ready**: Fully containerized for easy deployment
- 🔒 **Secure**: Runs as non-root user in container
- 🚀 **CI/CD Ready**: Includes Woodpecker CI pipelines for automated testing and deployment

## CI/CD Pipeline

This project includes comprehensive CI/CD pipelines using **Woodpecker CI**:

- ✅ **Automated Testing**: Code quality, linting, and security scans
- 🏗️ **Docker Builds**: Automated image building and testing
- 🚀 **Deployments**: Production deployment automation
- 📊 **Monitoring**: Health checks and status notifications

### Pipeline Features
- **Code Quality**: Black formatting, flake8 linting, import sorting
- **Security**: Bandit security scanning, dependency vulnerability checks
- **Testing**: Pytest test suite with coverage reporting
- **Docker**: Multi-stage builds with optimization
- **Deployment**: Automated production deployments on main branch

For detailed CI/CD setup instructions, see [WOODPECKER_CI_README.md](WOODPECKER_CI_README.md).

### Quick Development Commands

Use the included Makefile for common development tasks:

```bash
# Setup development environment
make setup

# Run tests and linting
make ci-test

# Build and test Docker image
make ci-build

# Format code
make format

# Run security scans
make security
```

## Prerequisites

- Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))
- OpenAI API Key ([OpenAI Platform](https://platform.openai.com/api-keys))
- Docker and Docker Compose (for containerized deployment)

## Bot Permissions

Your Discord bot needs the following permissions:
- `Use Slash Commands`
- `Manage Emojis and Stickers`
- `Add Reactions`
- `Read Message History`

## Quick Start with Docker

1. **Clone and navigate to the project**:
   ```bash
   git clone <your-repo-url>
   cd emoji_gen_bot
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual tokens
   ```

3. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

4. **Check logs**:
   ```bash
   docker-compose logs -f
   ```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_BOT_TOKEN` | Your Discord bot token | Yes |
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `GUILD_ID` | Discord server ID for faster command sync | No |

## Usage

1. **Invite the bot** to your Discord server with the required permissions
2. **Right-click any message** in your server
3. **Select "Generate Emoji Reaction"** from the context menu
4. **Fill in the modal**:
   - **Emoji Name**: Short name for the emoji (e.g., "happycat")
   - **Prompt**: Description of the emoji you want to generate
5. **Submit** and wait for the bot to generate and react with your custom emoji!

## Deployment on OCI Instance

### Method 1: Docker Compose (Recommended)

1. **Install Docker on your OCI instance**:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose -y
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker $USER
   ```

2. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd emoji_gen_bot
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   nano .env  # Add your tokens
   ```

4. **Deploy**:
   ```bash
   docker-compose up -d
   ```

### Method 2: Docker Build and Run

1. **Build the image**:
   ```bash
   docker build -t discord-emoji-bot .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     --name emoji-bot \
     --restart unless-stopped \
     -e DISCORD_BOT_TOKEN=your_token \
     -e OPENAI_API_KEY=your_key \
     -e GUILD_ID=your_guild_id \
     discord-emoji-bot
   ```

## Local Development

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your tokens
   ```

3. **Run the bot**:
   ```bash
   python discord_emoji.py
   ```

## Docker Configuration

The bot is configured with:
- **Base Image**: Python 3.11 slim
- **Security**: Runs as non-root user
- **Health Checks**: Built-in container health monitoring
- **Logging**: JSON file logging with rotation
- **Auto-restart**: Container restarts on failure

## Troubleshooting

### Common Issues

1. **"I don't have permission to add emojis"**
   - Ensure the bot has "Manage Emojis and Stickers" permission
   - Check that the server hasn't reached the emoji limit

2. **Commands not appearing**
   - Set `GUILD_ID` for faster sync during development
   - Wait up to 1 hour for global command sync

3. **Container not starting**
   - Check logs: `docker-compose logs`
   - Verify environment variables are set
   - Ensure tokens are valid

### Logs

View container logs:
```bash
# Docker Compose
docker-compose logs -f

# Direct Docker
docker logs -f emoji-bot
```

## Security Notes

- Never commit your `.env` file with real tokens
- Use environment variables for sensitive data
- The container runs as a non-root user for security
- Consider using Docker secrets for production deployments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review container logs
- Open an issue in the repository
