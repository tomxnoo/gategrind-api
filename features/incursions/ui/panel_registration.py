# Panel registration for Shadow Incursions
from shared.utils.panel_registry import register_panel
from features.incursions.ui.incursion_panel import IncursionPanel

# Register the incursion panel
register_panel(
    key="incursions",
    label="Shadow Incursions",
    emoji="🌑",
    panel_class=IncursionPanel
)