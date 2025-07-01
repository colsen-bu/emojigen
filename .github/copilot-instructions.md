<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Discord Emoji Bot Project

This is a Discord bot that generates custom emojis using OpenAI's DALL-E API and adds them as reactions to messages.

## Key Features
- Context menu command for generating emoji reactions
- Uses OpenAI DALL-E 3 for image generation
- Automatically adds emoji to server and reacts to message
- Cleans up emoji after use to save server space
- Dockerized for easy deployment

## Architecture
- Built with discord.py library
- Uses OpenAI Python SDK
- Async/await pattern throughout
- Modal-based user interaction
- Environment-based configuration

## Docker Deployment
- Multi-stage build with Python 3.11 slim
- Non-root user for security
- Health checks included
- Docker Compose for orchestration
- Optimized for OCI instance deployment
