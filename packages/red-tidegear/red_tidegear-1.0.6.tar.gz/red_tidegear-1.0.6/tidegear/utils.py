from typing import Callable, Optional, Union

from discord import Message
from discord.abc import MISSING, Messageable
from redbot.core import commands
from redbot.core.utils.chat_formatting import error


async def send_error(
    messeagable: Union[commands.Context, Messageable], /, content: Optional[str] = MISSING, func: Callable[[str], str] = error, **kwargs
) -> Message:
    """Send a message with the content wrapped in an error function.

    Args:
        messeagable (Union[commands.Context, Messageable]): The channel or context to send the message with.
        content (Optional[str]): The content of the message.
        func: (Callable[[str], str]): The function to use to wrap the message. Defaults to `redbot.core.utils.chat_formatting.error()`.
        **kwargs: Additional arguments to pass to `await messeagable.send()`.

    Returns:
        Message: The sent message.
    """
    if content:
        content = func(content)
    return await messeagable.send(content=content, **kwargs)
