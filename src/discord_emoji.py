"""Discord Emoji Bot - Generate custom emojis using OpenAI's DALL-E API."""

import os

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from openai import OpenAI

# Configuration from environment
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
GUILD_ID = os.environ.get("GUILD_ID")  # Optional for testing
RESPONSE_CHANNEL = os.environ.get("RESPONSE_CHANNEL")  # Optional response channel

openai_client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True


class EmojiBot(commands.Bot):
    """Discord bot for generating custom emojis using OpenAI's DALL-E API."""

    def __init__(self):
        """Initialize the EmojiBot with required intents and settings."""
        super().__init__(command_prefix="!", intents=intents)
        self.synced_guilds = set()

    async def setup_hook(self):
        """Set up the bot by adding commands and syncing to guilds."""
        self.tree.add_command(generate_emoji_reaction)

        # If GUILD_ID is specified, sync to that guild immediately (for testing)
        if GUILD_ID and GUILD_ID.strip():
            try:
                guild_id = int(GUILD_ID)
                await self.tree.sync(guild=discord.Object(id=guild_id))
                self.synced_guilds.add(guild_id)
                print(f"✅ Commands synced to test guild {guild_id}")
            except ValueError:
                print("⚠️  Invalid GUILD_ID format")

    async def on_guild_join(self, guild):
        """Sync commands immediately when bot joins a new server."""
        if guild.id not in self.synced_guilds:
            try:
                await self.tree.sync(guild=guild)
                self.synced_guilds.add(guild.id)
                print(f"✅ Commands synced to new guild: {guild.name} ({guild.id})")
            except discord.HTTPException as e:
                print(f"❌ Failed to sync commands to {guild.name}: {e}")

    async def on_ready(self):
        """Handle bot ready event and sync commands to all guilds."""
        print(f"✅ Logged in as {self.user}")
        print(f"📊 Connected to {len(self.guilds)} server(s)")

        # Sync commands to all current guilds if not already synced
        for guild in self.guilds:
            if guild.id not in self.synced_guilds:
                try:
                    await self.tree.sync(guild=guild)
                    self.synced_guilds.add(guild.id)
                    print(f"✅ Commands synced to existing guild: {guild.name}")
                except discord.HTTPException as e:
                    print(f"❌ Failed to sync to {guild.name}: {e}")


bot = EmojiBot()


async def get_response_channel(guild, current_channel):
    """Get the appropriate channel for bot responses."""
    # Hardcoded specific channel ID for bot responses
    target_channel_id = 992467592180670485
    channel = guild.get_channel(target_channel_id)
    if channel:
        perms = channel.permissions_for(guild.me)
        if perms.send_messages:
            return channel

    # Fallback: Check if bot can send messages in current channel
    permissions = current_channel.permissions_for(guild.me)
    if permissions.send_messages:
        return current_channel

    # Last resort: Find any channel where bot can send messages
    for channel in guild.text_channels:
        perms = channel.permissions_for(guild.me)
        if perms.send_messages:
            return channel

    return None


@bot.event
async def on_ready():
    """Handle bot ready event - delegated to bot class."""
    pass  # Handled in the bot class


@app_commands.context_menu(name="Generate Emoji Reaction")
async def generate_emoji_reaction(
    interaction: discord.Interaction, message: discord.Message
):
    """Context menu command to generate emoji reactions for messages."""
    await interaction.response.send_modal(EmojiPromptModal(target_message=message))


class EmojiPromptModal(discord.ui.Modal, title="Generate Emoji Reaction"):
    """Modal dialog for collecting emoji generation parameters."""

    prompt = discord.ui.TextInput(
        label="Prompt for Emoji Generation",
        style=discord.TextStyle.paragraph,
        placeholder="A cute smiling orange cat emoji",
    )

    def __init__(self, target_message: discord.Message):
        """Initialize modal with target message for emoji reaction."""
        super().__init__()
        self.target_message = target_message

    @staticmethod
    def sanitize_emoji_name(name: str, guild: discord.Guild) -> str:
        """Sanitize emoji name to meet Discord requirements and ensure uniqueness."""
        import re

        # Discord emoji name requirements:
        # - 2-32 characters
        # - Only alphanumeric characters and underscores
        # - Cannot start or end with underscore
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "", name.lower())
        sanitized = sanitized.strip("_")

        # Ensure it's not empty and within length limits
        if not sanitized or len(sanitized) < 2:
            sanitized = "custom_emoji"
        elif len(sanitized) > 32:
            sanitized = sanitized[:32].rstrip("_")

        # Ensure the name is unique within the guild
        existing_names = {emoji.name for emoji in guild.emojis}
        original_name = sanitized
        counter = 1
        while sanitized in existing_names:
            sanitized = f"{original_name}_{counter}"
            counter += 1
            if len(sanitized) > 32:  # Ensure it doesn't exceed the length limit
                sanitized = sanitized[:32].rstrip("_")

        return sanitized  # Ensure a valid sanitized name is returned

    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission and generate emoji reaction."""
        await interaction.response.defer(thinking=True, ephemeral=True)

        # Find appropriate response channel
        response_channel = await get_response_channel(
            interaction.guild, interaction.channel
        )

        if not response_channel:
            return await interaction.followup.send(
                "❌ I don't have permission to send messages in any channel.",
                ephemeral=True,
            )

        # Updated style injection for better emoji generation
        EMOJI_STYLE_PREFIX = (
            "A flat, high-contrast, minimalistic emoji design with ample negative space. "
            "Circular design, bold colors, clear outlines, and optimized for small sizes. "
            "Avoid excessive detail or background elements. Prompt: "
        )
        final_prompt = EMOJI_STYLE_PREFIX + self.prompt.value

        # Extract the first word from the prompt for the emoji name
        first_word = (
            self.prompt.value.split()[0] if self.prompt.value.split() else "emoji"
        )
        sanitized_name = self.sanitize_emoji_name(first_word, interaction.guild)

        # Generate image with GPT-Image-1
        try:
            import asyncio

            # Run the OpenAI call in a thread pool to avoid blocking
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: openai_client.images.generate(
                        model="dall-e-3",
                        prompt=final_prompt,
                        n=1,
                        quality="standard",
                        size="1024x1024",
                    )
                ),
                timeout=30.0,  # 30 second timeout
            )
            if not response.data or not response.data[0].url:
                return await interaction.followup.send(
                    "❌ No image URL returned from OpenAI", ephemeral=True
                )
            image_url = str(response.data[0].url)
        except asyncio.TimeoutError:
            return await interaction.followup.send(
                "❌ OpenAI API request timed out. Please try again.", ephemeral=True
            )
        except Exception as e:
            return await interaction.followup.send(
                f"❌ Failed to generate image: {e}", ephemeral=True
            )

        # Download and resize the generated image for emoji use
        try:
            timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(image_url) as resp:
                    if resp.status != 200:
                        return await interaction.followup.send(
                            "❌ Could not download image.", ephemeral=True
                        )
                    image_data = await resp.read()
        except asyncio.TimeoutError:
            return await interaction.followup.send(
                "❌ Image download timed out. Please try again.", ephemeral=True
            )
        except Exception as e:
            return await interaction.followup.send(
                f"❌ Failed to download image: {e}", ephemeral=True
            )

        # Resize image to 128x128 for optimal emoji size
        try:
            import io

            from PIL import Image

            # Open and resize the image
            image = Image.open(io.BytesIO(image_data))
            image = image.resize((128, 128), Image.Resampling.LANCZOS)

            # Convert to bytes for Discord
            output = io.BytesIO()
            image.save(output, format="PNG")
            image_data = output.getvalue()
        except Exception as e:
            # If PIL fails, use original image (Discord will auto-resize)
            print(f"⚠️ Image resize failed, using original: {e}")

        # Create custom emoji on the server
        try:
            emoji = await interaction.guild.create_custom_emoji(
                name=sanitized_name, image=image_data
            )
        except discord.Forbidden:
            return await interaction.followup.send(
                "❌ I don't have permission to add emojis.", ephemeral=True
            )
        except discord.HTTPException as e:
            return await interaction.followup.send(
                f"❌ Failed to create emoji '{sanitized_name}': {e}", ephemeral=True
            )

        # Add emoji reaction to the target message
        try:
            await self.target_message.add_reaction(emoji)

            # Send success message to the designated response channel
            success_message = (
                f"✅ **Success!! Emoji Generated from: `{self.prompt.value}`**"
            )
            await response_channel.send(success_message)

            # Send ephemeral confirmation to terminate the generating state
            await interaction.followup.send(
                "✅ Emoji generated and added!", ephemeral=True
            )

        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Failed to react: {e}", ephemeral=True)

        # Clean up emoji to save server space
        try:
            await emoji.delete()
        except discord.HTTPException:
            pass


@app_commands.command(
    name="generate_emoji", description="Generate a custom emoji using a prompt"
)
@app_commands.describe(prompt="The prompt for generating the emoji")
async def generate_emoji(interaction: discord.Interaction, prompt: str):
    """Slash command to generate a custom emoji."""
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Find appropriate response channel
    response_channel = await get_response_channel(
        interaction.guild, interaction.channel
    )

    if not response_channel:
        return await interaction.followup.send(
            "❌ I don't have permission to send messages in any channel.",
            ephemeral=True,
        )

    # Style injection for better emoji generation
    EMOJI_STYLE_PREFIX = (
        "A flat, high-contrast, minimalistic emoji design with ample negative space. "
        "Circular design, bold colors, clear outlines, and optimized for small sizes. "
        "Avoid excessive detail or background elements. Prompt: "
    )
    final_prompt = EMOJI_STYLE_PREFIX + prompt

    # Extract the first word from the prompt for the emoji name
    first_word = prompt.split()[0] if prompt.split() else "emoji"
    sanitized_name = EmojiPromptModal.sanitize_emoji_name(first_word, interaction.guild)

    # Generate image with GPT-Image-1
    try:
        import asyncio

        # Run the OpenAI call in a thread pool to avoid blocking
        response = await asyncio.wait_for(
            asyncio.to_thread(
                lambda: openai_client.images.generate(
                    model="dall-e-3",
                    prompt=final_prompt,
                    n=1,
                    quality="standard",
                    size="1024x1024",
                )
            ),
            timeout=30.0,  # 30 second timeout
        )
        if not response.data or not response.data[0].url:
            return await interaction.followup.send(
                "❌ No image URL returned from OpenAI", ephemeral=True
            )
        image_url = str(response.data[0].url)
    except asyncio.TimeoutError:
        return await interaction.followup.send(
            "❌ OpenAI API request timed out. Please try again.", ephemeral=True
        )
    except Exception as e:
        return await interaction.followup.send(
            f"❌ Failed to generate image: {e}", ephemeral=True
        )

    # Download and resize the generated image for emoji use
    try:
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    return await interaction.followup.send(
                        "❌ Could not download image.", ephemeral=True
                    )
                image_data = await resp.read()
    except asyncio.TimeoutError:
        return await interaction.followup.send(
            "❌ Image download timed out. Please try again.", ephemeral=True
        )
    except Exception as e:
        return await interaction.followup.send(
            f"❌ Failed to download image: {e}", ephemeral=True
        )

    # Resize image to 128x128 for optimal emoji size
    try:
        import io

        from PIL import Image

        # Open and resize the image
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((128, 128), Image.Resampling.LANCZOS)

        # Convert to bytes for Discord
        output = io.BytesIO()
        image.save(output, format="PNG")
        image_data = output.getvalue()
    except Exception as e:
        # If PIL fails, use original image (Discord will auto-resize)
        print(f"⚠️ Image resize failed, using original: {e}")

    # Create custom emoji on the server
    try:
        emoji = await interaction.guild.create_custom_emoji(
            name=sanitized_name, image=image_data
        )
    except discord.Forbidden:
        return await interaction.followup.send(
            "❌ I don't have permission to add emojis.", ephemeral=True
        )
    except discord.HTTPException as e:
        return await interaction.followup.send(
            f"❌ Failed to create emoji '{sanitized_name}': {e}", ephemeral=True
        )

    # Send success message to the designated response channel
    success_message = f"✅ **Success!! Emoji Generated from: `{prompt}`**"
    await response_channel.send(success_message)

    # Send ephemeral confirmation to terminate the generating state
    await interaction.followup.send("✅ Emoji generated and added!", ephemeral=True)

    # Clean up emoji to save server space
    try:
        await emoji.delete()
    except discord.HTTPException:
        pass


# Add the slash command to the bot
def setup(bot):
    """Add the generate_emoji slash command to the bot."""
    bot.tree.add_command(generate_emoji)


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
