# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ext import commands
import traceback
import functools
from typing import Callable, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error_msg = f"❌ Error in command `{ctx.command}`: {error}"
        print(error_msg)
        traceback.print_exception(type(error), error, error.__traceback__)

        try:
            await ctx.send("⚠️ An unexpected error occurred. Check logs or contact The Watcher.", ephemeral=True)
        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_error(self, event_method, *args, **kwargs):
        print(f"❌ Global error in `{event_method}`")
        traceback.print_exc()

# --- UNIVERSAL ERROR RECOVERY HELPERS ---

def handle_panel_errors(panel_name: str, category: str = "system", severity: str = "major"):
    """
    Decorator that automatically handles errors in panel methods with universal error recovery UI
    
    Usage:
    @handle_panel_errors("awakening", "api")
    async def my_panel_method(self):
        # Your code here
        pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {panel_name} panel method {func.__name__}: {e}")
                
                # Try to extract user from common patterns
                user = None
                if args and hasattr(args[0], 'view') and hasattr(args[0].view, 'user'):
                    user = args[0].view.user  # Button callback pattern
                elif args and hasattr(args[0], 'user'):
                    user = args[0].user  # View pattern
                elif len(args) > 1 and hasattr(args[1], 'user'):
                    user = args[1].user  # Function with user parameter
                
                if user:
                    from shared.utils.error_recovery import ErrorRecoveryBuilder, ErrorCategory
                    return (ErrorRecoveryBuilder(user, panel_name)
                            .with_error(str(e))
                            .with_category(category)
                            .with_severity(severity)
                            .with_retry_callback(lambda: func(*args, **kwargs))
                            .build())
                else:
                    # Fallback if we can't determine user
                    raise e
        return wrapper
    return decorator

async def quick_error_recovery(
    user: discord.User, 
    panel_name: str, 
    error: Exception, 
    category: str = "system",
    retry_func: Optional[Callable] = None
) -> Tuple[discord.Embed, discord.ui.View]:
    """
    Quick helper function to create error recovery UI with minimal code
    
    Usage:
    try:
        # Your code here
        pass
    except Exception as e:
        return await quick_error_recovery(user, "awakening", e, "api", retry_func)
    """
    from shared.utils.error_recovery import ErrorRecoveryBuilder
    
    # Auto-detect category based on error type
    if "api" in str(error).lower() or "connection" in str(error).lower():
        category = "api"
    elif "database" in str(error).lower() or "db" in str(error).lower():
        category = "database"
    elif "network" in str(error).lower() or "timeout" in str(error).lower():
        category = "network"
    elif "permission" in str(error).lower() or "forbidden" in str(error).lower():
        category = "permission"
    elif "validation" in str(error).lower() or "invalid" in str(error).lower():
        category = "validation"
    
    return (ErrorRecoveryBuilder(user, panel_name)
            .with_error(str(error))
            .with_category(category)
            .with_retry_callback(retry_func)
            .build())

# Context manager for automatic error handling
class PanelErrorContext:
    """
    Context manager for automatic error handling in panel operations
    
    Usage:
    async with PanelErrorContext(user, "awakening", "api") as ctx:
        # Your code here
        result = await some_api_call()
        ctx.set_retry(lambda: some_api_call())
        return result
    """
    
    def __init__(self, user: discord.User, panel_name: str, category: str = "system"):
        self.user = user
        self.panel_name = panel_name
        self.category = category
        self.retry_func = None
        
    def set_retry(self, retry_func: Callable):
        """Set the retry function for this operation"""
        self.retry_func = retry_func
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"Error in {self.panel_name} panel: {exc_val}")
            # Return the error recovery UI
            result = await quick_error_recovery(
                self.user, 
                self.panel_name, 
                exc_val, 
                self.category, 
                self.retry_func
            )
            # Store result for caller to access
            self._error_result = result
            return True  # Suppress the exception
        return False

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))