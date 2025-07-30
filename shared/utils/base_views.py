# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ui import View
from typing import Union, Optional

class BaseEphemeralView(View):
    """
    Base view class for ephemeral panel views.
    This avoids circular imports between common_views and panel modules.
    """
    def __init__(self, bot, user: Union[discord.User, discord.Member], timeout: Optional[float] = None):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.user = user

class SimpleFallbackView(View):
    """
    Simple fallback view for error states.
    Provides a clean view without any components.
    """
    def __init__(self, timeout: Optional[float] = 300):
        super().__init__(timeout=timeout)