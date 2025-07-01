# Woodpecker CI Secrets Configuration Template
# 
# This file documents the secrets that need to be configured in your Woodpecker CI
# for the Discord Emoji Bot pipeline to work properly.
#
# To add secrets in Woodpecker CI:
# 1. Go to your repository settings in Woodpecker
# 2. Navigate to the "Secrets" section
# 3. Add the following secrets:

# Required Secrets for Discord Bot:
DISCORD_BOT_TOKEN: 
  # Description: Your Discord bot token from Discord Developer Portal
  # Instructions: 
  #   1. Go to https://discord.com/developers/applications
  #   2. Select your bot application
  #   3. Go to "Bot" section
  #   4. Copy the token

OPENAI_API_KEY:
  # Description: Your OpenAI API key for DALL-E image generation
  # Instructions:
  #   1. Go to https://platform.openai.com/api-keys
  #   2. Create a new API key
  #   3. Copy the key (starts with 'sk-')

# Optional Secrets:
GUILD_ID:
  # Description: Discord Guild (server) ID for testing (optional)
  # Instructions:
  #   1. Enable Developer Mode in Discord
  #   2. Right-click your server
  #   3. Select "Copy Server ID"

RESPONSE_CHANNEL:
  # Description: Specific channel name or ID for bot responses (optional)

# Container Registry Secrets (if using external registry):
DOCKER_REGISTRY_URL:
  # Description: Docker registry URL (optional)

DOCKER_REGISTRY_USERNAME:
  # Description: Docker registry username (optional)

DOCKER_REGISTRY_PASSWORD:
  # Description: Docker registry password/token (optional)

# Deployment Secrets (for production deployment):
DEPLOY_HOST:
  # Description: Production server hostname/IP (optional)

DEPLOY_USER:
  # Description: SSH username for deployment (optional)
  # Example: "deploy"

DEPLOY_KEY:
  # Description: SSH private key for deployment (optional)
  # Note: Use SSH key authentication for security

# Notification Secrets (optional):
SLACK_WEBHOOK_URL:
  # Description: Slack webhook for notifications (optional)

DISCORD_WEBHOOK_URL:
  # Description: Discord webhook for notifications (optional)

# How to add secrets in Woodpecker CI:
# 1. Navigate to your repository in Woodpecker CI
# 2. Go to Settings > Secrets
# 3. Click "Add Secret"
# 4. Enter the secret name and value
# 5. Configure which events can access the secret
# 6. Save the secret

# Security Notes:
# - Never commit actual secret values to your repository
# - Use meaningful secret names that describe their purpose
# - Regularly rotate your secrets for security
# - Limit secret access to necessary events only
# - Monitor secret usage in pipeline logs (values will be masked)
