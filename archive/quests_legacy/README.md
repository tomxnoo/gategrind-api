# Quest System Legacy Files

This directory contains the original 
quest system files that were moved during 
the quest system rework.

## What was moved and when
- **Date**: January 2025
- **Reason**: Quest system rework based 
on Gemini 2.5 Pro recommendations
- **Source**: All files from `features/
quests/`

## Original Structure

features/quests/
├── init .py
├── cog.py
├── logic/
│   ├── init .py
│   ├── daily_quests/
│   │   ├── init .py
│   │   ├── daily_quest_logic.py
│   │   ├── enhanced_daily_quests.py
│   │   └── generate_daily_quests.py
│   ├── movement_defs.py
│   ├── quest_data.py
│   ├── quest_templates.py
│   └── weekly_quests/
│       ├── init .py
│       ├── reroll_weekly_contracts.py
│       └── weekly_quest_logic.py
└── ui/
├── init .py
├── daily/
│   ├── init .py
│   ├── daily_quest_ansi.py
│   ├── daily_quest_panel.py
│   ├── daily_quest_ui.py
│   └── daily_selector_view.py
├── daily_quest_panel.py
├── quest_abandon_panel_ui.py
├── quest_abandon_ui.py
├── quest_accept_decline.py
├── quest_completion_ui.py
├── quest_dropdown.py
├── quest_panel.py
├── quest_panel_common.py
├── quest_reroll_ui.py
└── weekly/
├── init .py
├── weekly_contract_ansi.py
└── weekly_contract_panel.py



## New Quest System
The new quest system is being built with:
- `core/game_data/exercise_library.py` - 
Unified exercise library
- `features/awakening/logic/quest_engine.
py` - New quest generation engine
- `features/awakening/ui/awakening_panel.
py` - Enhanced awakening panel
- `features/quests_v2/` - New quest 
system implementation

## Migration Notes
- These files are preserved for reference 
and potential rollback
- Imports have been temporarily updated 
to use legacy paths
- Once migration is complete, these files 
can be safely removed

## DO NOT DELETE
These files should be kept until the new 
quest system is fully tested and deployed.
