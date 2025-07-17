"""
Universal Error Recovery UI System
Provides consistent, thematic error handling across all bot panels
"""

import discord
from typing import Dict, Any, Optional, List, Tuple, Callable
from shared.utils.headers import get_system_status_header
from shared.utils.ui_styles import get_panel_sub_header
import logging

logger = logging.getLogger(__name__)

class ErrorSeverity:
    """Error severity levels with corresponding styling"""
    MINOR = "minor"      # Yellow warning, recoverable
    MAJOR = "major"      # Red error, requires action
    CRITICAL = "critical" # Red with special handling, system-level

class ErrorCategory:
    """Error categories for contextual messaging"""
    API = "api"
    DATABASE = "database"
    NETWORK = "network"
    VALIDATION = "validation"
    PERMISSION = "permission"
    SYSTEM = "system"
    QUEST = "quest"
    AWAKENING = "awakening"
    INCURSION = "incursion"
    LOGGING = "logging"

class ErrorRecoveryBuilder:
    """Builder for creating consistent error recovery UIs"""
    
    def __init__(self, user: discord.User, panel_name: str):
        self.user = user
        self.panel_name = panel_name
        self.error_msg = ""
        self.severity = ErrorSeverity.MAJOR
        self.category = ErrorCategory.SYSTEM
        self.recovery_options = []
        self.technical_details = []
        self.custom_title = None
        self.custom_status = None
        self.retry_callback = None
        
    def with_error(self, error_msg: str) -> 'ErrorRecoveryBuilder':
        """Set the main error message"""
        self.error_msg = error_msg
        return self
        
    def with_severity(self, severity: str) -> 'ErrorRecoveryBuilder':
        """Set error severity (minor, major, critical)"""
        self.severity = severity
        return self
        
    def with_category(self, category: str) -> 'ErrorRecoveryBuilder':
        """Set error category for contextual messaging"""
        self.category = category
        return self
        
    def with_recovery_option(self, option: str) -> 'ErrorRecoveryBuilder':
        """Add a recovery option to the list"""
        self.recovery_options.append(option)
        return self
        
    def with_technical_detail(self, detail: str) -> 'ErrorRecoveryBuilder':
        """Add technical detail for debugging"""
        self.technical_details.append(detail)
        return self
        
    def with_custom_title(self, title: str) -> 'ErrorRecoveryBuilder':
        """Set custom error title instead of default"""
        self.custom_title = title
        return self
        
    def with_custom_status(self, status: str) -> 'ErrorRecoveryBuilder':
        """Set custom status message"""
        self.custom_status = status
        return self
        
    def with_retry_callback(self, callback: Callable) -> 'ErrorRecoveryBuilder':
        """Set callback function for retry button"""
        self.retry_callback = callback
        return self
        
    def build(self) -> Tuple[discord.Embed, discord.ui.View]:
        """Build the error recovery UI"""
        return build_error_recovery_ui(
            user=self.user,
            panel_name=self.panel_name,
            error_msg=self.error_msg,
            severity=self.severity,
            category=self.category,
            recovery_options=self.recovery_options,
            technical_details=self.technical_details,
            custom_title=self.custom_title,
            custom_status=self.custom_status,
            retry_callback=self.retry_callback
        )

def get_category_context(category: str) -> Dict[str, str]:
    """Get contextual information for error categories"""
    contexts = {
        ErrorCategory.API: {
            "emoji": "🔌",
            "system": "API INTERFACE",
            "description": "External service communication failed",
            "default_recovery": ["Check API service status", "Verify network connectivity", "Retry the operation"]
        },
        ErrorCategory.DATABASE: {
            "emoji": "🗄️",
            "system": "DATA CORE",
            "description": "Database operation encountered an issue",
            "default_recovery": ["Check database connectivity", "Verify data integrity", "Retry the operation"]
        },
        ErrorCategory.NETWORK: {
            "emoji": "🌐",
            "system": "NETWORK LAYER",
            "description": "Network communication disrupted",
            "default_recovery": ["Check internet connection", "Verify server status", "Wait and retry"]
        },
        ErrorCategory.VALIDATION: {
            "emoji": "⚠️",
            "system": "VALIDATION ENGINE",
            "description": "Input validation failed",
            "default_recovery": ["Check input format", "Verify required fields", "Review constraints"]
        },
        ErrorCategory.PERMISSION: {
            "emoji": "🔒",
            "system": "ACCESS CONTROL",
            "description": "Insufficient permissions for operation",
            "default_recovery": ["Check user permissions", "Contact administrator", "Verify access level"]
        },
        ErrorCategory.QUEST: {
            "emoji": "⚔️",
            "system": "QUEST ENGINE",
            "description": "Quest system operation failed",
            "default_recovery": ["Retry quest generation", "Check quest parameters", "Verify user eligibility"]
        },
        ErrorCategory.AWAKENING: {
            "emoji": "🌅",
            "system": "AWAKENING CORE",
            "description": "Awakening ritual encountered disruption",
            "default_recovery": ["Retry the awakening process", "Check system connectivity", "Wait a moment and try again"]
        },
        ErrorCategory.INCURSION: {
            "emoji": "⚡",
            "system": "INCURSION MATRIX",
            "description": "Incursion system malfunction detected",
            "default_recovery": ["Refresh incursion data", "Check system status", "Retry operation"]
        },
        ErrorCategory.LOGGING: {
            "emoji": "📊",
            "system": "LOGGING INTERFACE",
            "description": "Activity logging system disrupted",
            "default_recovery": ["Retry logging operation", "Check data format", "Verify system status"]
        },
        ErrorCategory.SYSTEM: {
            "emoji": "🔧",
            "system": "CORE SYSTEM",
            "description": "System-level operation failed",
            "default_recovery": ["Check system status", "Verify configuration", "Contact support if persistent"]
        }
    }
    
    return contexts.get(category, contexts[ErrorCategory.SYSTEM])

def get_severity_styling(severity: str) -> Dict[str, str]:
    """Get styling information for error severity levels"""
    styles = {
        ErrorSeverity.MINOR: {
            "color": "\x1b[1;33m",  # Yellow
            "status_emoji": "⚠️",
            "status_text": "WARNING",
            "embed_color": discord.Color.yellow()
        },
        ErrorSeverity.MAJOR: {
            "color": "\x1b[1;31m",  # Red
            "status_emoji": "❌",
            "status_text": "ERROR",
            "embed_color": discord.Color.red()
        },
        ErrorSeverity.CRITICAL: {
            "color": "\x1b[1;35m",  # Magenta
            "status_emoji": "🚨",
            "status_text": "CRITICAL",
            "embed_color": discord.Color.from_rgb(255, 0, 255)
        }
    }
    
    return styles.get(severity, styles[ErrorSeverity.MAJOR])

def build_error_recovery_ui(
    user: discord.User,
    panel_name: str,
    error_msg: str,
    severity: str = ErrorSeverity.MAJOR,
    category: str = ErrorCategory.SYSTEM,
    recovery_options: List[str] = None,
    technical_details: List[str] = None,
    custom_title: str = None,
    custom_status: str = None,
    retry_callback: Callable = None
) -> Tuple[discord.Embed, discord.ui.View]:
    """Build a universal error recovery UI"""
    
    # Get contextual information
    category_info = get_category_context(category)
    severity_info = get_severity_styling(severity)
    
    # Build header and sub-header
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header(panel_name)
    
    # Build title and status
    title = custom_title or f"{panel_name.title()} Disrupted"
    status = custom_status or f"{severity_info['status_emoji']} {severity_info['status_text']}"
    
    # Build recovery options
    if not recovery_options:
        recovery_options = category_info["default_recovery"]
    
    recovery_list = ""
    for i, option in enumerate(recovery_options):
        if i == len(recovery_options) - 1:  # Last item
            recovery_list += f"└─ {option}"
        else:
            recovery_list += f"├─ {option}\n"
    
    # Build technical details
    tech_details = ""
    if technical_details:
        for detail in technical_details:
            tech_details += f"{detail}\n"
    else:
        tech_details = f"The {panel_name} system encountered an issue.\nYour request was recorded for analysis.\n"
    
    # Truncate error message if too long
    display_error = error_msg[:100] + "..." if len(error_msg) > 100 else error_msg
    
    # Build content
    content = (
        f"```ansi\n"
        f"{header}\n"
        f"{sub_header}\n\n"
        f"{severity_info['color']}● {title}\x1b[0m\n"
        f"Status: {severity_info['color']}{status}\x1b[0m\n"
        f"Engine: {severity_info['color']}{category_info['emoji']} {category_info['system']}\x1b[0m\n"
        f"Impact: \x1b[1;37m{category_info['description']}\x1b[0m\n\n"
        f"\x1b[1;37m🛠️ Technical Details:\x1b[0m\n"
        f"{tech_details}\n"
        f"\x1b[1;37m🔄 Recovery Options:\x1b[0m\n"
        f"{recovery_list}\n\n"
        f"\x1b[1;37m💡 Error Details:\x1b[0m\n"
        f"{display_error}\n\n"
        f"──────────────────────────\n"
        f"```"
    )
    
    # Create embed
    embed = discord.Embed(
        description=content,
        color=severity_info["embed_color"]
    )
    embed.set_footer(text=f"Shadow Archive • {panel_name.title()} • Error Recovery")
    
    # Create view with recovery options
    view = ErrorRecoveryView(user, panel_name, retry_callback)
    
    return embed, view

class ErrorRecoveryView(discord.ui.View):
    """Universal error recovery view with consistent actions"""
    
    def __init__(self, user: discord.User, panel_name: str, retry_callback: Callable = None):
        super().__init__(timeout=300)  # 5 minute timeout
        self.user = user
        self.panel_name = panel_name
        self.retry_callback = retry_callback
        
        # Add panel dropdown first
        from shared.utils.common_views import EphemeralPanelSelect
        self.add_item(EphemeralPanelSelect(None, user.id))  # Bot will be set by caller
        
        # Add retry button if callback provided
        if retry_callback:
            self.add_item(RetryOperationButton(retry_callback))
        
        # Add return to panel button
        self.add_item(ReturnToPanelButton(panel_name))

class RetryOperationButton(discord.ui.Button):
    """Button to retry the failed operation"""
    
    def __init__(self, retry_callback: Callable):
        super().__init__(
            label="🔄 Retry Operation",
            style=discord.ButtonStyle.primary,
            emoji="🔄"
        )
        self.retry_callback = retry_callback
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            result = await self.retry_callback()
            if result:
                embed, view = result
                await interaction.edit_original_response(embed=embed, view=view)
            else:
                await interaction.followup.send("❌ Retry failed. Please try again later.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in retry callback: {e}")
            await interaction.followup.send("❌ Retry encountered an error. Please try again later.", ephemeral=True)

class ReturnToPanelButton(discord.ui.Button):
    """Button to return to the main panel"""
    
    def __init__(self, panel_name: str):
        super().__init__(
            label=f"⬅️ Return to {panel_name.title()}",
            style=discord.ButtonStyle.secondary,
            emoji="⬅️"
        )
        self.panel_name = panel_name
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Import and call the appropriate panel builder
        try:
            if self.panel_name == "awakening":
                from features.awakening.ui.awakening_panel import build_enhanced_awakening_embed, EnhancedAwakeningMainView
                embed = await build_enhanced_awakening_embed(self.view.bot, self.view.user)
                view = EnhancedAwakeningMainView(self.view.bot, self.view.user)
            elif self.panel_name == "incursions":
                from features.incursions.ui.incursion_panel import build_incursion_embed, IncursionMainView
                embed = await build_incursion_embed(self.view.bot, self.view.user)
                view = IncursionMainView(self.view.bot, self.view.user)
            elif self.panel_name == "logging":
                from features.logging.ui.logging_panel import build_logging_embed, LoggingMainView
                embed = await build_logging_embed(self.view.bot, self.view.user)
                view = LoggingMainView(self.view.bot, self.view.user)
            else:
                # Generic fallback - return to system hub
                from features.system.ui.system_hub_panel import build_system_hub_embed, SystemHubMainView
                embed = await build_system_hub_embed(self.view.bot, self.view.user)
                view = SystemHubMainView(self.view.bot, self.view.user)
            
            await interaction.edit_original_response(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error returning to panel {self.panel_name}: {e}")
            await interaction.followup.send("❌ Could not return to panel. Please use the dropdown menu.", ephemeral=True)

# Convenience functions for common error scenarios
def create_api_error(user: discord.User, panel_name: str, error_msg: str, retry_callback: Callable = None):
    """Create an API error recovery UI"""
    return (ErrorRecoveryBuilder(user, panel_name)
            .with_error(error_msg)
            .with_category(ErrorCategory.API)
            .with_severity(ErrorSeverity.MAJOR)
            .with_retry_callback(retry_callback)
            .build())

def create_database_error(user: discord.User, panel_name: str, error_msg: str, retry_callback: Callable = None):
    """Create a database error recovery UI"""
    return (ErrorRecoveryBuilder(user, panel_name)
            .with_error(error_msg)
            .with_category(ErrorCategory.DATABASE)
            .with_severity(ErrorSeverity.MAJOR)
            .with_retry_callback(retry_callback)
            .build())

def create_network_error(user: discord.User, panel_name: str, error_msg: str, retry_callback: Callable = None):
    """Create a network error recovery UI"""
    return (ErrorRecoveryBuilder(user, panel_name)
            .with_error(error_msg)
            .with_category(ErrorCategory.NETWORK)
            .with_severity(ErrorSeverity.MINOR)
            .with_retry_callback(retry_callback)
            .build())

def create_validation_error(user: discord.User, panel_name: str, error_msg: str, retry_callback: Callable = None):
    """Create a validation error recovery UI"""
    return (ErrorRecoveryBuilder(user, panel_name)
            .with_error(error_msg)
            .with_category(ErrorCategory.VALIDATION)
            .with_severity(ErrorSeverity.MINOR)
            .with_retry_callback(retry_callback)
            .build())

def create_permission_error(user: discord.User, panel_name: str, error_msg: str):
    """Create a permission error recovery UI"""
    return (ErrorRecoveryBuilder(user, panel_name)
            .with_error(error_msg)
            .with_category(ErrorCategory.PERMISSION)
            .with_severity(ErrorSeverity.MAJOR)
            .with_recovery_option("Contact server administrator")
            .with_recovery_option("Check your role permissions")
            .with_recovery_option("Verify access requirements")
            .build())