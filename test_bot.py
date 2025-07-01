"""
Basic tests for the Discord Emoji Bot

These tests validate the bot's core functionality and ensure
dependencies are properly configured.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
import discord_emoji


class TestEmojiBot:
    """Test cases for the EmojiBot class"""

    def test_imports(self):
        """Test that all required modules can be imported"""
        import discord
        import aiohttp
        from openai import OpenAI
        from PIL import Image
        assert True  # If we get here, imports work

    def test_bot_initialization(self):
        """Test that the bot can be initialized"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'DISCORD_BOT_TOKEN': 'test_token',
            'OPENAI_API_KEY': 'test_key'
        }):
            # Import should work with mocked env vars
            import importlib
            importlib.reload(discord_emoji)
            assert True

    @patch.dict(os.environ, {
        'DISCORD_BOT_TOKEN': 'test_token',
        'OPENAI_API_KEY': 'test_key'
    })
    def test_emoji_name_sanitization(self):
        """Test emoji name sanitization functionality"""
        # Create a mock modal to test the sanitization method
        mock_message = Mock()
        modal = discord_emoji.EmojiPromptModal(target_message=mock_message)
        
        # Test cases
        test_cases = [
            ("hello world", "hello_world"),
            ("test@emoji#name!", "testemojiname"),
            ("_underscore_", "underscore"),
            ("123numbers", "123numbers"),
            ("a" * 50, "a" * 32),  # Test length limit
            ("", "custom_emoji"),  # Test empty name fallback
            ("special-chars!@#", "specialchars"),
        ]
        
        for input_name, expected in test_cases:
            result = modal.sanitize_emoji_name(input_name)
            assert isinstance(result, str)
            assert len(result) >= 2
            assert len(result) <= 32
            # Check that result only contains valid characters
            assert all(c.isalnum() or c == '_' for c in result)
            assert not result.startswith('_')
            assert not result.endswith('_')

    @patch.dict(os.environ, {
        'DISCORD_BOT_TOKEN': 'test_token',
        'OPENAI_API_KEY': 'test_key'
    })
    async def test_get_response_channel(self):
        """Test the response channel selection logic"""
        # Mock guild and channels
        mock_guild = Mock()
        mock_current_channel = Mock()
        mock_bot_member = Mock()
        
        # Mock permissions
        mock_permissions = Mock()
        mock_permissions.send_messages = True
        mock_current_channel.permissions_for.return_value = mock_permissions
        mock_guild.me = mock_bot_member
        
        # Test current channel permission check
        result = await discord_emoji.get_response_channel(mock_guild, mock_current_channel)
        assert result == mock_current_channel

    def test_configuration_loading(self):
        """Test that configuration is loaded from environment"""
        required_vars = ['DISCORD_BOT_TOKEN', 'OPENAI_API_KEY']
        
        for var in required_vars:
            # These should be set in the environment during testing
            # or should raise appropriate errors if missing
            assert hasattr(discord_emoji, var.replace('DISCORD_', '').replace('OPENAI_', ''))


class TestDockerConfiguration:
    """Test Docker-related configuration"""

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists and is readable"""
        assert os.path.exists('Dockerfile')
        with open('Dockerfile', 'r') as f:
            content = f.read()
            assert 'FROM python:3.11-slim' in content
            assert 'discord_emoji.py' in content

    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists and is valid"""
        assert os.path.exists('docker-compose.yml')
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
            assert 'discord-emoji-bot' in content
            assert 'DISCORD_BOT_TOKEN' in content
            assert 'OPENAI_API_KEY' in content

    def test_requirements_file(self):
        """Test that requirements.txt contains necessary packages"""
        assert os.path.exists('requirements.txt')
        with open('requirements.txt', 'r') as f:
            content = f.read()
            required_packages = ['discord.py', 'aiohttp', 'openai', 'Pillow']
            for package in required_packages:
                assert package in content


if __name__ == "__main__":
    pytest.main([__file__])
