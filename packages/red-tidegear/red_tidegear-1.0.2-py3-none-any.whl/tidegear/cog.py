# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

from typing import List

from discord import Guild, User
from red_commons.logging import RedTraceLogger, getLogger
from redbot.core import commands, data_manager
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import bold, humanize_list
from typing_extensions import override

from .metadata import CogMetadata
from .version import meta


class Cog(commands.Cog):
    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        # this is fine because Red itself will fail if the client isn't logged in way before this cog would be loaded
        self.me: User = bot.get_user(bot.user.id)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        path = data_manager.bundled_data_path(self) / "meta.json"
        if not path.exists():
            msg = f"There is no metadata file located at {path}!"
            raise FileNotFoundError(msg)
        self.metadata: CogMetadata = CogMetadata.from_json(self.__cog_name__, path)
        self.logger: RedTraceLogger = getLogger(f"red.{self.metadata.repository.name}.{self.__cog_name__}")

    @override
    def format_help_for_context(self, ctx: commands.Context) -> str:
        base = (super().format_help_for_context(ctx) or "").rstrip("\n") + "\n"
        parts: List[str] = [base]
        parts.append(f"{bold('Cog Version:')} [{self.metadata.version}]({self.metadata.repository.url})")
        author_label = "Authors:" if len(self.metadata.authors) >= 2 else "Author:"
        parts.append(f"{bold(author_label)} {humanize_list([author.markdown for author in self.metadata.authors])}")
        if self.metadata.documentation is not None:
            parts.append(f"{bold('Documentation:')} {self.metadata.documentation}")
        parts.append(f"{bold('Tidegear Version:')} {meta.markdown}")
        return "\n".join(parts)

    async def get_or_fetch_user(self, user_id: int) -> User:
        """Retrieve a user from the internal cache, or fetch it if it cannot be found.
        Use this sparingly, as the `fetch_user` endpoint has a strict ratelimit.

        Args:
            user_id (int): The ID of the user to retrieve.

        Raises:
            discord.NotFound: If the user does not exist.
            discord.HTTPException: Fetching the user failed.

        Returns:
            User: The retrieved user.
        """
        user = self.bot.get_user(user_id)
        if not user:
            user = await self.bot.fetch_user(user_id)
        return user

    async def get_or_fetch_guild(self, guild_id: int) -> Guild:
        """Retrieve a guild from the internal cache, or fetch it if it cannot be found.
        Use this sparingly, as the `fetch_guild` endpoint has a strict ratelimit.

        Args:
            guild_id (int): The ID of the guild to retrieve.

        Raises:
            discord.NotFound: If the guild does not exist or the bot does not have access to it.
            discord.HTTPException: Fetching the guild failed.

        Returns:
            Guild: The retrieved guild.
        """
        guild = self.bot.get_guild(guild_id)
        if not guild:
            guild = await self.bot.fetch_guild(guild_id)
        return guild
