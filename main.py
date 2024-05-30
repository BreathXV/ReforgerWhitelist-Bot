import logging, logging.handlers
import os, typing, traceback
import sqlite3
import aiohttp

import discord
from discord.ext import commands


class Client(commands.Bot):
    """Creates the bot instance.

    Args:
        commands (object): Attaches command(s) back to the bot.
    """

    def __init__(
        self,
        prefix: str,
        ext_dir: str = "extensions",
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Initiates the Client class.

        Args:
            prefix (str): The prefix used by the bot.
            ext_dir (str, optional): Where the extensions/cogs are located. Defaults to "extensions".
        """
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(
            *args,
            **kwargs,
            command_prefix=commands.when_mentioned_or(prefix),
            intents=intents,
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ext_dir = ext_dir
        self.synced = False

    async def _load_extensions(self) -> None:
        """Loads and attaches all extensions (cogs) to the bot."""
        if not os.path.isdir(self.ext_dir):
            self.logger.error(f"Extension directory {self.ext_dir} does not exist.")
            return
        for filename in os.listdir(self.ext_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    await self.load_extension(f"{self.ext_dir}.{filename[:-3]}")
                    self.logger.info(f"Loaded extension {filename[:-3]}")
                except commands.ExtensionError:
                    self.logger.error(
                        f"Failed to load extension {filename[:-3]}\n{traceback.format_exc()}"
                    )

    async def on_error(
        self, event_method: str, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """When an error occurs, invoke a error log message.

        Args:
            event_method (str): The function where the error occurred.
        """
        self.logger.error(
            f"An error occurred in {event_method}.\n{traceback.format_exc()}"
        )

    async def on_ready(self) -> None:
        """Logs when the bot is ready."""
        self.logger.info(f"Logged in as {self.user} ({self.user.id})")

    async def setup_hook(self) -> None:
        """Sets up the hook and syncs the command tree."""
        self.client = aiohttp.ClientSession()
        await self._load_extensions()
        if not self.synced:
            await self.tree.sync()
            self.synced = not self.synced
            self.logger.info("Synced command tree")


def main() -> None:
    """Starts the bot."""
    logging.basicConfig(
        level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
    )
    bot = Client(prefix="!", ext_dir="extensions")

    bot.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    print(os.path.exists(os.getenv("DATABASE_PATH")))
    create_database()
    main()
