# easycord/context.py
import asyncio

class BaseContext:
    """A base context to share the reply logic."""
    def __init__(self, bot, interaction_or_message):
        self._bot = bot
        self._source = interaction_or_message

    @property
    def author(self):
        return self._source.author

    @property
    def user(self):
        return self._source.author # Alias for author

    @property
    def channel(self):
        return self._source.channel

    @property
    def guild(self):
        return self._source.guild

    def reply(self, content, ephemeral=False, **kwargs):
        """
        Replies to the interaction or message.
        This safely calls the async reply method from a synchronous user function.
        """
        # For interactions (slash commands, buttons)
        if hasattr(self._source, "response"):
            coro = self._source.response.send_message(content, ephemeral=ephemeral, **kwargs)
        # For regular messages
        else:
            coro = self._source.reply(content, **kwargs)

        # Schedule the coroutine on the bot's event loop from the sync thread
        asyncio.run_coroutine_threadsafe(coro, self._bot.loop)


class MessageContext(BaseContext):
    def __init__(self, bot, message):
        super().__init__(bot, message)
        self.message = message
        # Parse arguments from the message content
        parts = message.content.split()
        self.args = parts[1:] if len(parts) > 1 else []


class InteractionContext(BaseContext):
    def __init__(self, bot, interaction):
        super().__init__(bot, interaction)
        self.interaction = interaction