"""Discord Emoji Bot - Generate custom emojis using OpenAI's DALL-E API."""

import glob
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

# Get the path to the static folder
STATIC_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))

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
        # Commands will be added after bot initialization
        print(
            f"🔧 Setup hook called. Registered commands: "
            f"{len(self.tree.get_commands())}"
        )

        # If GUILD_ID is specified, sync to that guild immediately (for testing)
        if GUILD_ID and GUILD_ID.strip():
            try:
                guild_id = int(GUILD_ID)
                # Clear old commands first, then sync new ones
                print(f"🔄 Clearing old commands for guild {guild_id}...")
                self.tree.clear_commands(guild=discord.Object(id=guild_id))
                synced = await self.tree.sync(guild=discord.Object(id=guild_id))
                self.synced_guilds.add(guild_id)
                print(
                    f"✅ Commands synced to test guild {guild_id}: "
                    f"{len(synced)} commands"
                )
                for cmd in synced:
                    print(f"  - {cmd.name} ({cmd.type.name})")
            except ValueError:
                print("⚠️  Invalid GUILD_ID format")

    async def on_guild_join(self, guild):
        """Sync commands immediately when bot joins a new server."""
        if guild.id not in self.synced_guilds:
            try:
                # Clear any existing commands first
                self.tree.clear_commands(guild=guild)
                await self.tree.sync(guild=guild)
                self.synced_guilds.add(guild.id)
                print(f"✅ Commands synced to new guild: {guild.name} ({guild.id})")
            except discord.HTTPException as e:
                print(f"❌ Failed to sync commands to {guild.name}: {e}")

    async def on_ready(self):
        """Handle bot ready event and sync commands to all guilds."""
        print(f"✅ Logged in as {self.user}")
        print(f"📊 Connected to {len(self.guilds)} server(s)")
        print(f"🔧 Total registered commands: {len(self.tree.get_commands())}")

        # List all registered commands for debugging
        for cmd in self.tree.get_commands():
            print(f"  - {cmd.name} ({cmd.type.name})")

        # Sync commands to all current guilds if not already synced
        for guild in self.guilds:
            if guild.id not in self.synced_guilds:
                try:
                    # Clear old commands first to avoid conflicts
                    print(f"🔄 Clearing old commands for guild: {guild.name}")
                    self.tree.clear_commands(guild=guild)
                    synced = await self.tree.sync(guild=guild)
                    self.synced_guilds.add(guild.id)
                    print(
                        f"✅ Commands synced to existing guild: {guild.name} "
                        f"({len(synced)} commands)"
                    )
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
async def add_emoji_reaction(
    interaction: discord.Interaction, message: discord.Message
):
    """Context menu command to add emoji reactions - either generated or static."""
    try:
        # Check if interaction has already been responded to
        if interaction.response.is_done():
            print("⚠️ Context menu interaction already responded to")
            return

        # Try to defer the interaction, but handle timeouts gracefully
        try:
            await interaction.response.defer(ephemeral=True)

            view = EmojiSelectionView(target_message=message)
            embed = discord.Embed(
                title="🎭 Add Emoji Reaction",
                description="Choose how you want to add an emoji reaction:",
                color=0x5865F2,
            )
            # Use followup.send() because the interaction has been deferred
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        except discord.NotFound:
            # If defer fails due to unknown interaction, try direct response
            print("⚠️ Context menu defer failed, attempting direct response")

            view = EmojiSelectionView(target_message=message)
            embed = discord.Embed(
                title="🎭 Add Emoji Reaction",
                description="Choose how you want to add an emoji reaction:",
                color=0x5865F2,
            )

            try:
                await interaction.response.send_message(
                    embed=embed, view=view, ephemeral=True
                )
            except (discord.NotFound, discord.HTTPException) as e:
                print(f"❌ Failed to respond to context menu interaction: {e}")
                return

    except Exception as e:
        print(f"❌ Unexpected error in add_emoji_reaction: {e}")
        # Try to send an error message if possible
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred while processing your request. Please try again.",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    "❌ An error occurred while processing your request. Please try again.",
                    ephemeral=True,
                )
        except Exception:
            pass  # If we can't even send an error message, just log it


class EmojiSelectionView(discord.ui.View):
    """View for selecting between generating or using static emojis."""

    def __init__(self, target_message: discord.Message):
        """Initialize the emoji selection view for the target message."""
        super().__init__(timeout=300)  # 5 minute timeout
        self.target_message = target_message

    @discord.ui.button(label="🎨 Generate New Emoji", style=discord.ButtonStyle.primary)
    async def generate_emoji(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Show the generate emoji modal."""
        try:
            # Check if interaction has already been responded to
            if interaction.response.is_done():
                print("⚠️ Generate emoji button interaction already responded to")
                return

            await interaction.response.send_modal(
                EmojiPromptModal(target_message=self.target_message)
            )
        except discord.NotFound:
            print(
                "⚠️ Generate emoji button interaction failed due to unknown interaction"
            )
        except Exception as e:
            print(f"❌ Error in generate emoji button: {e}")

    @discord.ui.button(label="🖼️ Use Static Emoji", style=discord.ButtonStyle.secondary)
    async def use_static_emoji(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Show the static emoji search modal."""
        try:
            # Check if interaction has already been responded to
            if interaction.response.is_done():
                print("⚠️ Static emoji button interaction already responded to")
                return

            await interaction.response.send_modal(
                StaticEmojiSearchModal(
                    target_message=self.target_message, original_interaction=interaction
                )
            )
        except discord.NotFound:
            print("⚠️ Static emoji button interaction failed due to unknown interaction")
        except Exception as e:
            print(f"❌ Error in static emoji button: {e}")


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
            "A large, centered emoji design filling 100% of the image canvas. "
            "Flat vector style with high contrast and bold, vibrant colors. "
            "Minimal background, maximum zoom on the emoji subject. "
            "Clean, thick outlines and simple geometric shapes. "
            "Optimized for visibility at small sizes with no fine details. "
            "Square format, no borders or margins. Prompt: "
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

            # Open and zoom in on the center of the image
            image = Image.open(io.BytesIO(image_data))

            # Calculate crop box for center zoom (crop to 70% of original size)
            width, height = image.size
            crop_size = min(width, height) * 0.7
            left = (width - crop_size) / 2
            top = (height - crop_size) / 2
            right = left + crop_size
            bottom = top + crop_size

            # Crop to center and then resize
            image = image.crop((left, top, right, bottom))
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


def get_static_emoji_files():
    """Get list of static emoji files from the static folder."""
    global STATIC_FOLDER  # Declare global at the beginning

    print(f"🔍 Searching for static files in: {STATIC_FOLDER}")
    print(f"🔍 Current working directory: {os.getcwd()}")
    print(f"🔍 Directory contents: {os.listdir('.')}")

    if not os.path.exists(STATIC_FOLDER):
        print(f"❌ Static folder does not exist at: {STATIC_FOLDER}")
        # Try alternative paths
        alternative_paths = [
            os.path.join(os.getcwd(), "static"),
            "/app/static",
            os.path.abspath("static"),
        ]
        for alt_path in alternative_paths:
            print(f"🔍 Trying alternative path: {alt_path}")
            if os.path.exists(alt_path):
                print(f"✅ Found static folder at: {alt_path}")
                STATIC_FOLDER = alt_path
                break
        else:
            print("❌ No static folder found in any location.")
            return []

    # Support common image formats
    patterns = ["*.png", "*.jpg", "*.jpeg", "*.gif"]
    files = []
    for pattern in patterns:
        pattern_files = glob.glob(os.path.join(STATIC_FOLDER, pattern))
        print(f"🔍 Pattern {pattern} found {len(pattern_files)} files")
        files.extend(pattern_files)

    print(f"✅ Found {len(files)} static files total.")
    if files:
        print(f"📁 Sample files: {files[:5]}")  # Show first 5 files

    # Sort files and return just the filenames
    return sorted([os.path.basename(f) for f in files])


def search_static_emojis(query):
    """Search static emoji files by query string."""
    all_files = get_static_emoji_files()
    if not query.strip():
        return all_files[:25]  # Return first 25 if no query

    query_lower = query.lower()

    # Search for files that contain the query in their name
    matches = []
    for filename in all_files:
        if query_lower in filename.lower():
            matches.append(filename)

    return matches[:25]  # Limit to 25 results for Discord select menu


class StaticEmojiView(discord.ui.View):
    """View for selecting static emoji to react with."""

    def __init__(
        self,
        target_message: discord.Message,
        search_results: list,
        query: str = "",
        original_interaction=None,
    ):
        """Initialize the static emoji view with search results."""
        super().__init__(timeout=300)  # 5 minute timeout
        self.target_message = target_message
        self.search_results = search_results
        self.query = query
        self.original_interaction = original_interaction

        # Add select menu if we have results
        if search_results:
            self.add_item(
                StaticEmojiSelect(search_results, target_message, original_interaction)
            )

    @discord.ui.button(label="🔍 Search Again", style=discord.ButtonStyle.secondary)
    async def search_again(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Show the search modal again."""
        try:
            # Check if interaction has already been responded to
            if interaction.response.is_done():
                print("⚠️ Search again button interaction already responded to")
                return

            await interaction.response.send_modal(
                StaticEmojiSearchModal(self.target_message, self.original_interaction)
            )
        except discord.NotFound:
            print("⚠️ Search again button interaction failed due to unknown interaction")
        except Exception as e:
            print(f"❌ Error in search again button: {e}")

    def _create_embed(self):
        """Create embed for current page."""
        if self.query:
            title = f"🖼️ Static Emoji Search Results: '{self.query}'"
            description = f"Found {len(self.search_results)} emojis"
        else:
            title = "🖼️ Static Emojis"
            description = f"Showing {len(self.search_results)} emojis"

        embed = discord.Embed(
            title=title,
            description=description,
            color=0x5865F2,
        )

        if len(self.search_results) > 25:
            embed.add_field(
                name="⚠️ Limited Results",
                value="Only showing first 25 results. Try a more specific search.",
                inline=False,
            )

        return embed


class StaticEmojiSelect(discord.ui.Select):
    """Select menu for choosing a static emoji."""

    def __init__(
        self,
        emoji_files: list,
        target_message: discord.Message,
        original_interaction=None,
    ):
        """Initialize the static emoji select menu with available emoji files."""
        self.target_message = target_message
        self.original_interaction = original_interaction

        # Create options from emoji files
        options = []
        for filename in emoji_files[:25]:  # Discord limit of 25 options
            # Extract a clean name from filename for display
            clean_name = (
                filename.replace("_", " ")
                .replace(".png", "")
                .replace(".jpg", "")
                .replace(".jpeg", "")
                .replace(".gif", "")
            )

            # Create a preview-style label with emoji
            if "cat" in filename.lower():
                emoji_preview = "🐱"
            elif "dog" in filename.lower():
                emoji_preview = "🐶"
            elif "smile" in filename.lower() or "happy" in filename.lower():
                emoji_preview = "😊"
            elif "sad" in filename.lower():
                emoji_preview = "😢"
            elif "heart" in filename.lower():
                emoji_preview = "❤️"
            elif "star" in filename.lower():
                emoji_preview = "⭐"
            elif "fire" in filename.lower():
                emoji_preview = "🔥"
            elif "logo" in filename.lower() or "brand" in filename.lower():
                emoji_preview = "🏷️"
            elif "circle" in filename.lower():
                emoji_preview = "⚪"
            elif "arrow" in filename.lower():
                emoji_preview = "➡️"
            elif "check" in filename.lower() or "tick" in filename.lower():
                emoji_preview = "✅"
            elif "cross" in filename.lower() or "x" in filename.lower():
                emoji_preview = "❌"
            elif "warning" in filename.lower():
                emoji_preview = "⚠️"
            elif "info" in filename.lower():
                emoji_preview = "ℹ️"
            else:
                emoji_preview = "🖼️"

            # Create display label with emoji preview
            display_label = f"{emoji_preview} {clean_name}"
            if len(display_label) > 100:
                display_label = display_label[:97] + "..."

            options.append(
                discord.SelectOption(
                    label=display_label[:100],  # Discord label limit
                    value=filename,
                    description=(
                        f"📁 {filename[:100]}"
                        if len(filename) <= 100
                        else f"📁 {filename[:97]}..."
                    ),
                )
            )

        super().__init__(
            placeholder="Choose a static emoji to react with...",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        """Handle emoji selection."""
        try:
            # Check if interaction has already been responded to
            if interaction.response.is_done():
                print("⚠️ Static emoji selection interaction already responded to")
                return

            try:
                await interaction.response.defer(thinking=True, ephemeral=True)
            except discord.NotFound:
                print(
                    "⚠️ Static emoji selection defer failed due to unknown interaction"
                )
                return
            except Exception as e:
                print(f"❌ Static emoji selection defer failed: {e}")
                return

            selected_file = self.values[0]
            file_path = os.path.join(STATIC_FOLDER, selected_file)

            print(f"🔍 Looking for selected file: {selected_file}")
            print(f"🔍 Full file path: {file_path}")
            print(f"🔍 File exists: {os.path.exists(file_path)}")

            if not os.path.exists(file_path):
                # Update the original message instead of sending a new one
                if self.original_interaction:
                    return await self.original_interaction.edit_original_response(
                        content=f"❌ Selected emoji file not found at: {file_path}",
                        embed=None,
                        view=None,
                    )
                else:
                    return await interaction.followup.send(
                        f"❌ Selected emoji file not found at: {file_path}",
                        ephemeral=True,
                    )

            # Find appropriate response channel
            response_channel = await get_response_channel(
                interaction.guild, interaction.channel
            )

            if not response_channel:
                # Update the original message instead of sending a new one
                if self.original_interaction:
                    return await self.original_interaction.edit_original_response(
                        content="❌ I don't have permission to send messages in any channel.",
                        embed=None,
                        view=None,
                    )
                else:
                    return await interaction.followup.send(
                        "❌ I don't have permission to send messages in any channel.",
                        ephemeral=True,
                    )

            # Create emoji name from filename
            base_name = os.path.splitext(selected_file)[0]
            sanitized_name = EmojiPromptModal.sanitize_emoji_name(
                base_name, interaction.guild
            )

            # Read the image file
            try:
                with open(file_path, "rb") as f:
                    image_data = f.read()
            except Exception as e:
                # Update the original message instead of sending a new one
                if self.original_interaction:
                    return await self.original_interaction.edit_original_response(
                        content=f"❌ Failed to read emoji file: {e}",
                        embed=None,
                        view=None,
                    )
                else:
                    return await interaction.followup.send(
                        f"❌ Failed to read emoji file: {e}", ephemeral=True
                    )

            # Resize image if it's not a GIF and is larger than 128x128
            if not selected_file.lower().endswith(".gif"):
                try:
                    import io

                    from PIL import Image

                    image = Image.open(io.BytesIO(image_data))
                    if image.size[0] > 128 or image.size[1] > 128:
                        image = image.resize((128, 128), Image.Resampling.LANCZOS)
                        output = io.BytesIO()
                        image.save(output, format="PNG")
                        image_data = output.getvalue()
                except Exception as e:
                    print(f"⚠️ Image resize failed, using original: {e}")

            # Create custom emoji on the server
            try:
                emoji = await interaction.guild.create_custom_emoji(
                    name=sanitized_name, image=image_data
                )
            except discord.Forbidden:
                # Update the original message instead of sending a new one
                if self.original_interaction:
                    return await self.original_interaction.edit_original_response(
                        content="❌ I don't have permission to add emojis.",
                        embed=None,
                        view=None,
                    )
                else:
                    return await interaction.followup.send(
                        "❌ I don't have permission to add emojis.", ephemeral=True
                    )
            except discord.HTTPException as e:
                # Update the original message instead of sending a new one
                if self.original_interaction:
                    return await self.original_interaction.edit_original_response(
                        content=f"❌ Failed to create emoji '{sanitized_name}': {e}",
                        embed=None,
                        view=None,
                    )
                else:
                    return await interaction.followup.send(
                        f"❌ Failed to create emoji '{sanitized_name}': {e}",
                        ephemeral=True,
                    )

            # Add emoji reaction to the target message
            try:
                await self.target_message.add_reaction(emoji)

                # Send success message to the designated response channel
                success_message = f"✅ **Static Emoji Added: `{selected_file}`**"
                await response_channel.send(success_message)

                # Update the original message with success
                if self.original_interaction:
                    await self.original_interaction.edit_original_response(
                        content="✅ Static emoji added as reaction!",
                        embed=None,
                        view=None,
                    )
                else:
                    await interaction.followup.send(
                        "✅ Static emoji added as reaction!", ephemeral=True
                    )

            except discord.HTTPException as e:
                # Update the original message instead of sending a new one
                if self.original_interaction:
                    await self.original_interaction.edit_original_response(
                        content=f"❌ Failed to react: {e}", embed=None, view=None
                    )
                else:
                    await interaction.followup.send(
                        f"❌ Failed to react: {e}", ephemeral=True
                    )

            # Clean up emoji to save server space
            try:
                await emoji.delete()
            except discord.HTTPException:
                pass

        except Exception as e:
            print(f"❌ Unexpected error in static emoji selection: {e}")
            try:
                # Update the original message instead of sending a new one
                if self.original_interaction:
                    await self.original_interaction.edit_original_response(
                        content="❌ An error occurred while adding the static emoji. "
                        "Please try again.",
                        embed=None,
                        view=None,
                    )
                elif not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ An error occurred while adding the static emoji. Please try again.",
                        ephemeral=True,
                    )
                else:
                    await interaction.followup.send(
                        "❌ An error occurred while adding the static emoji. Please try again.",
                        ephemeral=True,
                    )
            except Exception:
                pass  # If we can't even send an error message, just log it


class StaticEmojiSearchModal(discord.ui.Modal, title="Search Static Emojis"):
    """Modal dialog for searching static emojis."""

    search_query = discord.ui.TextInput(
        label="Search for Static Emoji",
        style=discord.TextStyle.short,
        placeholder="Enter keywords to search for (e.g., cat, smile, logo)",
        required=False,
        max_length=100,
    )

    def __init__(self, target_message: discord.Message, original_interaction=None):
        """Initialize the static emoji search modal for the target message."""
        super().__init__()
        self.target_message = target_message
        self.original_interaction = original_interaction

    async def on_submit(self, interaction: discord.Interaction):
        """Handle search submission."""
        try:
            # Check if interaction has already been responded to
            if interaction.response.is_done():
                print("⚠️ Static emoji search modal interaction already responded to")
                return

            try:
                await interaction.response.defer(thinking=True, ephemeral=True)
            except discord.NotFound:
                print(
                    "⚠️ Static emoji search modal defer failed due to unknown interaction"
                )
                return
            except Exception as e:
                print(f"❌ Static emoji search modal defer failed: {e}")
                return

            query = self.search_query.value.strip()

            if query:
                search_results = search_static_emojis(query)
            else:
                # If no query, show first 25 emojis
                search_results = get_static_emoji_files()[:25]

            if not search_results:
                # Update the original message instead of sending a new one
                if self.original_interaction:
                    return await self.original_interaction.edit_original_response(
                        content=f"❌ No static emojis found for query: `{query}`\n"
                        f"Available emojis: {len(get_static_emoji_files())} total",
                        embed=None,
                        view=None,
                    )
                else:
                    return await interaction.followup.send(
                        f"❌ No static emojis found for query: `{query}`\n"
                        f"Available emojis: {len(get_static_emoji_files())} total",
                        ephemeral=True,
                    )

            # Create view with search results
            view = StaticEmojiView(
                self.target_message, search_results, query, self.original_interaction
            )
            embed = view._create_embed()

            # Update the original message instead of sending a new one
            if self.original_interaction:
                await self.original_interaction.edit_original_response(
                    content=None, embed=embed, view=view
                )
            else:
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        except Exception as e:
            print(f"❌ Unexpected error in static emoji search modal: {e}")
            try:
                # Update the original message instead of sending a new one
                if self.original_interaction:
                    await self.original_interaction.edit_original_response(
                        content="❌ An error occurred while searching for static emojis. "
                        "Please try again.",
                        embed=None,
                        view=None,
                    )
                elif not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ An error occurred while searching for static emojis. Please try again.",
                        ephemeral=True,
                    )
                else:
                    await interaction.followup.send(
                        "❌ An error occurred while searching for static emojis. Please try again.",
                        ephemeral=True,
                    )
            except Exception:
                pass  # If we can't even send an error message, just log it


@bot.command(name="sync_commands")
@commands.is_owner()
async def sync_commands(ctx):
    """Manual command to sync all app commands (owner only)."""
    try:
        # Clear and sync for the current guild
        bot.tree.clear_commands(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"✅ Synced {len(synced)} commands to {ctx.guild.name}")
        for cmd in synced:
            print(f"  - {cmd.name} ({cmd.type.name})")
    except Exception as e:
        await ctx.send(f"❌ Failed to sync commands: {e}")


# Register all commands with the bot
print("🔧 Registering commands...")
bot.tree.add_command(add_emoji_reaction)
print("  ✅ Added: Generate Emoji Reaction (context menu)")
print(f"🔧 Total commands registered: {len(bot.tree.get_commands())}")


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
