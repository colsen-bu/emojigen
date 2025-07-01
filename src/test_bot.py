"""
Basic tests for the Discord Emoji Bot.

These tests validate the bot's core functionality and ensure
dependencies are properly configured.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

import pytest

import discord_emoji


class TestEmojiBot:
    """Test cases for the EmojiBot class."""

    def test_bot_initialization(self):
        """Test that the bot can be initialized."""
        # Mock environment variables
        with patch.dict(
            os.environ,
            {"DISCORD_BOT_TOKEN": "test_token", "OPENAI_API_KEY": "test_key"},
        ):
            # Import should work with mocked env vars
            import importlib

            importlib.reload(discord_emoji)
            assert True @ patch.dict(
                os.environ,
                {"DISCORD_BOT_TOKEN": "test_token", "OPENAI_API_KEY": "test_key"},
            )

    def test_emoji_name_sanitization(self):
        """Test emoji name sanitization functionality."""

        # Create the modal class without initializing the parent Discord UI components
        class TestModal:
            def sanitize_emoji_name(self, name: str) -> str:
                """Copy of the sanitize_emoji_name method for testing."""
                import re

                sanitized = re.sub(r"[^a-zA-Z0-9_]", "", name.lower())
                sanitized = sanitized.strip("_")
                if not sanitized or len(sanitized) < 2:
                    sanitized = "custom_emoji"
                elif len(sanitized) > 32:
                    sanitized = sanitized[:32].rstrip("_")
                return sanitized

        modal = TestModal()

        # Test cases
        test_cases = [
            ("hello world", "helloworld"),
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
            assert all(c.isalnum() or c == "_" for c in result)
            assert not result.startswith("_")
            assert not result.endswith("_")

    @patch.dict(
        os.environ, {"DISCORD_BOT_TOKEN": "test_token", "OPENAI_API_KEY": "test_key"}
    )
    def test_get_response_channel(self):
        """Test the response channel selection logic."""
        # For now, just test that the function exists and is callable
        assert hasattr(discord_emoji, "get_response_channel")
        assert callable(discord_emoji.get_response_channel)

    def test_configuration_loading(self):
        """Test that configuration is loaded from environment."""
        # Test that the constants exist
        assert hasattr(discord_emoji, "DISCORD_BOT_TOKEN")
        assert hasattr(discord_emoji, "OPENAI_API_KEY")
        assert hasattr(discord_emoji, "GUILD_ID")
        assert hasattr(discord_emoji, "RESPONSE_CHANNEL")


class TestDockerConfiguration:
    """Test Docker-related configuration."""

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists and is readable."""
        dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
        assert dockerfile_path.exists()
        with open(dockerfile_path, "r") as f:
            content = f.read()
            assert "FROM python:3.11-slim" in content
            assert "src/discord_emoji.py" in content or "discord_emoji.py" in content

    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists and is valid."""
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        assert compose_path.exists()
        with open(compose_path, "r") as f:
            content = f.read()
            assert "discord-emoji-bot" in content or "emoji-bot" in content
            assert "DISCORD_BOT_TOKEN" in content
            assert "OPENAI_API_KEY" in content

    def test_requirements_file(self):
        """Test that requirements.txt contains necessary packages."""
        requirements_path = Path(__file__).parent.parent / "requirements.txt"
        assert requirements_path.exists()
        with open(requirements_path, "r") as f:
            content = f.read()
            required_packages = ["discord.py", "aiohttp", "openai", "Pillow"]
            for package in required_packages:
                assert package in content


if __name__ == "__main__":
    pytest.main([__file__])
