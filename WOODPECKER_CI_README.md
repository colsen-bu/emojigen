# Woodpecker CI Setup for Discord Emoji Bot

This document explains how to set up and use Woodpecker CI for the Discord Emoji Bot project.

## 📋 Overview

This project includes a comprehensive Woodpecker CI pipeline that:

- ✅ **Code Quality**: Runs linting, formatting checks, and security scans
- 🏗️ **Build**: Creates Docker images for the bot
- 🧪 **Test**: Validates functionality and dependencies
- 🚀 **Deploy**: Handles production deployments
- 📦 **Package**: Creates deployment artifacts

## 🗂️ Pipeline Files

```
.woodpecker.yml              # Main pipeline configuration
.woodpecker/
├── test.yml                 # Quick test pipeline
├── deploy.yml               # Production deployment pipeline
└── secrets-template.md      # Documentation for required secrets
```

## 🚀 Getting Started

### 1. Prerequisites

- Woodpecker CI server set up and running
- Repository connected to Woodpecker CI
- Required secrets configured (see [Secrets Setup](#secrets-setup))

### 2. Pipeline Triggers

The pipelines trigger on:
- **Push** to any branch
- **Pull requests**
- **Tags** (for releases)
- **Manual** execution

### 3. Pipeline Stages

#### Main Pipeline (`.woodpecker.yml`)

1. **Lint**: Code formatting and style checks
2. **Security Scan**: Vulnerability and security analysis
3. **Build**: Docker image creation
4. **Test Container**: Validate Docker container functionality
5. **Package**: Create deployment artifacts
6. **Deploy**: Production deployment (main branch only)
7. **Notify**: Pipeline status notifications

#### Test Pipeline (`.woodpecker/test.yml`)

- Quick validation for development
- Syntax checking
- Docker build verification

#### Deploy Pipeline (`.woodpecker/deploy.yml`)

- Production-focused deployment
- Health checks
- Container management
- Cleanup operations

## 🔐 Secrets Setup

Configure these secrets in your Woodpecker CI repository settings:

### Required Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DISCORD_BOT_TOKEN` | Discord bot token | `YOUR_BOT_TOKEN_HERE` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-YOUR_API_KEY_HERE` |

### Optional Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `GUILD_ID` | Discord server ID for testing | `123456789012345678` |
| `RESPONSE_CHANNEL` | Bot response channel | `bot-responses` |

### How to Add Secrets

1. Go to your repository in Woodpecker CI
2. Navigate to **Settings** > **Secrets**
3. Click **Add Secret**
4. Enter the secret name and value
5. Configure event permissions
6. Save the secret

## 🛠️ Local Development

### Running Tests Locally

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run code formatting
black discord_emoji.py

# Run import sorting
isort discord_emoji.py

# Run linting
flake8 discord_emoji.py --max-line-length=100

# Run security scan
bandit -r .
safety check

# Run tests
pytest test_bot.py -v
```

### Testing Docker Build

```bash
# Build the image
docker build -t emoji-bot:test .

# Test the container
docker run --rm -e DISCORD_BOT_TOKEN=test -e OPENAI_API_KEY=test emoji-bot:test python -c "import discord_emoji; print('Success!')"
```

## 📊 Pipeline Status

### Understanding Pipeline Results

- **✅ Green**: All checks passed, ready for deployment
- **❌ Red**: Pipeline failed, check logs for details
- **🟡 Yellow**: Pipeline running or pending

### Common Pipeline Issues

#### Import Errors
**Issue**: Missing dependencies  
**Solution**: Ensure `requirements.txt` is up to date

#### Docker Build Failures
**Issue**: Dockerfile syntax or dependency issues  
**Solution**: Test Docker build locally first

#### Permission Errors
**Issue**: Bot lacks Discord permissions  
**Solution**: Check bot permissions in Discord server

#### Secret Access Errors
**Issue**: Missing or incorrect secrets  
**Solution**: Verify secrets in Woodpecker CI settings

## 🚀 Deployment

### Automatic Deployment

Deployments happen automatically when:
- Code is pushed to the `main` branch
- All pipeline stages pass successfully
- Required secrets are available

### Manual Deployment

You can manually trigger deployment:
1. Go to your repository in Woodpecker CI
2. Click **Run Pipeline**
3. Select the deploy pipeline
4. Provide any required parameters

### Deployment Process

1. **Pre-deployment checks**: Validate environment
2. **Build production image**: Create optimized Docker image
3. **Deploy with docker-compose**: Update running containers
4. **Health check**: Verify deployment success
5. **Cleanup**: Remove old images

## 📈 Monitoring

### Pipeline Logs

- View detailed logs for each pipeline step
- Check for errors or warnings
- Monitor resource usage

### Bot Health

The pipeline includes health checks:
- Container startup validation
- Discord connection verification
- OpenAI API accessibility

## 🔧 Customization

### Adding New Pipeline Steps

1. Edit `.woodpecker.yml`
2. Add new step in appropriate location
3. Test changes on a feature branch
4. Merge when validated

### Environment-Specific Pipelines

Create additional pipeline files:
- `.woodpecker/staging.yml` - Staging environment
- `.woodpecker/feature.yml` - Feature branch testing

### Custom Notifications

Add notification steps:
```yaml
- name: slack-notify
  image: plugins/slack
  settings:
    webhook: ${SLACK_WEBHOOK}
    channel: deployments
    message: "Bot deployed successfully!"
```

## 🆘 Troubleshooting

### Pipeline Won't Start

1. Check repository connection to Woodpecker CI
2. Verify `.woodpecker.yml` syntax
3. Ensure required secrets are configured

### Build Failures

1. Review pipeline logs
2. Test Docker build locally
3. Check dependency versions
4. Validate environment variables

### Deployment Issues

1. Verify server access and permissions
2. Check Docker daemon status
3. Validate network connectivity
4. Review container logs

## 📚 Additional Resources

- [Woodpecker CI Documentation](https://woodpecker-ci.org/docs/)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Docker Documentation](https://docs.docker.com/)

## 🤝 Contributing

When contributing to this project:

1. Create a feature branch
2. Make your changes
3. Test locally first
4. Push and create a pull request
5. Wait for pipeline validation
6. Merge when approved

The CI pipeline will automatically validate your changes and provide feedback on any issues.
