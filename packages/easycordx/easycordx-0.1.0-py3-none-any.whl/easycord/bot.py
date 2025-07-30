# easycord/bot.py
import disnake
from disnake.ext import commands
import asyncio
import functools
import inspect
from .context import MessageContext, InteractionContext

class Bot:
    def __init__(self, token, prefix="!"):
        if not token:
            raise ValueError("A bot token is required.")
        self.token = token
        
        intents = disnake.Intents.default()
        intents.message_content = True # Required for reading message content
        intents.members = True # Required for on_member_join

        self._bot = commands.Bot(command_prefix=prefix, intents=intents)
        self._ready_callbacks = []
        self._message_handlers = []
        self._member_join_handlers = []
        self._commands = {}
        self._button_handlers = {}

        # Register internal event handlers
        self._bot.event(self.on_ready)
        self._bot.event(self.on_message)
        self._bot.event(self.on_member_join)
        self._bot.event(self.on_interaction)

    @property
    def user(self):
        return self._bot.user

    @property
    def loop(self):
        return self._bot.loop

    def run(self):
        """Starts the bot."""
        self._bot.run(self.token)

    # --- Internal Async Event Handlers (Hidden from User) ---

    async def on_ready(self):
        for callback, args, kwargs in self._ready_callbacks:
            # Run user's sync code in a thread pool to avoid blocking
            await self.loop.run_in_executor(None, functools.partial(callback, *args, **kwargs))

    async def on_message(self, message):
        if message.author == self._bot.user:
            return

        # 1. Check for commands first
        if message.content.startswith(self._bot.command_prefix):
            parts = message.content.split()
            cmd_name = parts[0][len(self._bot.command_prefix):]
            if cmd_name in self._commands:
                cmd = self._commands[cmd_name]
                ctx = MessageContext(self, message)
                
                # Handle simple "respond" commands
                if cmd['respond']:
                    await message.reply(cmd['respond'])
                # Handle function-based commands
                elif cmd['callback']:
                    # Check if args are expected
                    sig = inspect.signature(cmd['callback'])
                    params_needed = len(sig.parameters) - 1 # Subtract 1 for ctx
                    if len(ctx.args) >= params_needed:
                        await self.loop.run_in_executor(None, cmd['callback'], ctx, *ctx.args)
                    else:
                        await message.reply(f"Error: Command '{cmd_name}' needs {params_needed} argument(s).")
                # Handle commands with buttons
                elif cmd['button_text']:
                    button_id = f"easycord_btn_{cmd_name}_{message.id}"
                    self._button_handlers[button_id] = cmd['on_click']
                    
                    view = disnake.ui.View(timeout=180) # View times out after 3 mins
                    button = disnake.ui.Button(label=cmd['button_text'], custom_id=button_id, style=disnake.ButtonStyle.primary)
                    view.add_item(button)
                    
                    await message.reply(cmd['text'], view=view)
            return # Stop processing if it was a command

        # 2. Check for general message handlers
        for handler in self._message_handlers:
            if (handler['if_text'] and message.content.lower() == handler['if_text'].lower()) or \
               (handler['if_contains'] and handler['if_contains'].lower() in message.content.lower()):
                await message.channel.send(handler['respond'])
                break # Respond only once

    async def on_member_join(self, member):
        for handler in self._member_join_handlers:
             await self.loop.run_in_executor(None, handler, member)

    async def on_interaction(self, interaction: disnake.Interaction):
        if interaction.type == disnake.InteractionType.component:
            custom_id = interaction.data.custom_id
            if custom_id in self._button_handlers:
                handler = self._button_handlers[custom_id]
                ctx = InteractionContext(self, interaction)
                await self.loop.run_in_executor(None, handler, ctx)


    # --- User-Facing API Methods ---
    
    def send_message(self, channel_id, content):
        """Proactively sends a message to a specific channel."""
        async def _send():
            channel = self._bot.get_channel(channel_id)
            if channel:
                await channel.send(content)
        asyncio.run_coroutine_threadsafe(_send(), self.loop)

    def when_ready(self, callback, *args, **kwargs):
        self._ready_callbacks.append((callback, args, kwargs))

    def on(self, event_type, respond=None, if_text=None, if_contains=None, callback=None):
        if event_type.lower() == "message":
            self._message_handlers.append({
                "respond": respond,
                "if_text": if_text,
                "if_contains": if_contains
            })
        elif event_type.lower() == "member_join":
            if callback:
                self._member_join_handlers.append(callback)

    def command(self, name, callback=None, respond=None, button_text=None, on_click=None):
        cmd_data = {
            'name': name,
            'callback': callback,
            'respond': respond,
            'text': respond if button_text else None,
            'button_text': button_text,
            'on_click': on_click
        }
        self._commands[name] = cmd_data

    def auto_reply(self, trigger_text, response_text):
        """A simple alias for on('message', if_text=...)."""
        self.on("message", respond=response_text, if_text=trigger_text)