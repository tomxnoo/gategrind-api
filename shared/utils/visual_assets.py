import random
import os
from pathlib import Path

# Define anime icon themes and their file mappings
ANIME_ICON_THEMES = {
    "death_note": {
        "files": ["Death Note.ico", "Death Note alt.ico"],
        "mood": "dark",
        "description": "Dark and mysterious themes"
    },
    "bleach": {
        "files": ["Bleach.ico", "Bleach alt.ico"],
        "mood": "action",
        "description": "Soul reaper themes"
    },
    "code_geass": {
        "files": ["Code Geass.ico", "Code Geass alt.ico"],
        "mood": "strategic",
        "description": "Strategic and royal themes"
    },
    "soul_eater": {
        "files": ["Soul Eater.ico", "Soul Eater alt.ico"],
        "mood": "dark",
        "description": "Soul harvesting themes"
    },
    "naruto": {
        "files": ["Naruto.ico", "Naruto Shippuuden.ico"],
        "mood": "ninja",
        "description": "Ninja and shadow themes"
    },
    "tokyo_ghoul": {
        "files": ["Tokyo Ghoul.ico"],
        "mood": "horror",
        "description": "Dark urban themes"
    },
    "psycho_pass": {
        "files": ["Psycho Pass.ico", "Psycho Pass alt.ico"],
        "mood": "cyberpunk",
        "description": "Dystopian future themes"
    },
    "akame_ga_kill": {
        "files": ["Akagame ga Kill.ico"],
        "mood": "assassin",
        "description": "Assassin and revolution themes"
    }
}

def get_anime_icon_path(theme: str = None, mood: str = None) -> str:
    """Get a random anime icon path based on theme or mood"""
    base_path = Path("attached_assets")

    available_files = []

    if theme and theme in ANIME_ICON_THEMES:
        # Get specific theme
        theme_data = ANIME_ICON_THEMES[theme]
        for filename in theme_data["files"]:
            # Search through all token packs
            for pack in ["Token Anime Pack", "Token Anime Pack 2", "Token Anime Pack 3", "Token Anime Pack 4"]:
                file_path = base_path / pack / "ICO" / filename
                if file_path.exists():
                    available_files.append(str(file_path))

    elif mood:
        # Get by mood
        for theme_key, theme_data in ANIME_ICON_THEMES.items():
            if theme_data["mood"] == mood:
                for filename in theme_data["files"]:
                    for pack in ["Token Anime Pack", "Token Anime Pack 2", "Token Anime Pack 3", "Token Anime Pack 4"]:
                        file_path = base_path / pack / "ICO" / filename
                        if file_path.exists():
                            available_files.append(str(file_path))

    else:
        # Get random from all available
        for theme_data in ANIME_ICON_THEMES.values():
            for filename in theme_data["files"]:
                for pack in ["Token Anime Pack", "Token Anime Pack 2", "Token Anime Pack 3", "Token Anime Pack 4"]:
                    file_path = base_path / pack / "ICO" / filename
                    if file_path.exists():
                        available_files.append(str(file_path))

    if available_files:
        return random.choice(available_files)

    return None

def get_evolution_icon(level: int) -> str:
    """Get appropriate anime icon for evolution level"""
    if level >= 50:
        return get_anime_icon_path(mood="cyberpunk")  # Divine level
    elif level >= 40:
        return get_anime_icon_path(theme="death_note")  # Mythic level
    elif level >= 30:
        return get_anime_icon_path(theme="bleach")  # Legend level
    elif level >= 20:
        return get_anime_icon_path(theme="soul_eater")  # Master level
    elif level >= 15:
        return get_anime_icon_path(theme="akame_ga_kill")  # Expert level
    elif level >= 10:
        return get_anime_icon_path(theme="naruto")  # Adept level
    elif level >= 5:
        return get_anime_icon_path(theme="tokyo_ghoul")  # Apprentice level
    else:
        return get_anime_icon_path(mood="dark")  # Novice level

def get_quest_completion_icon() -> str:
    """Get random icon for quest completion"""
    return get_anime_icon_path(mood="action")

def get_buff_icon(buff_type: str) -> str:
    """Get appropriate icon for buff type"""
    if "shadow" in buff_type.lower():
        return get_anime_icon_path(mood="dark")
    elif "void" in buff_type.lower():
        return get_anime_icon_path(mood="horror")
    elif "phantom" in buff_type.lower():
        return get_anime_icon_path(theme="bleach")
    else:
        return get_anime_icon_path(mood="strategic")

def get_level_up_icon(level: int) -> str:
    """Get appropriate icon for level up"""
    return get_evolution_icon(level)

def get_random_visual_asset(asset_type: str = "general") -> str:
    """Get a random visual asset URL or emoji"""
    assets = {
        "general": [
            "🌟", "✨", "💫", "🔮", "🌙", "⚡", "🔥", "💎", "🌊", "🍃"
        ],
        "level_up": [
            "🎆", "🎇", "✨", "🌟", "💫", "🔥", "⚡", "🎊", "🎉", "👑"
        ],
        "quest": [
            "🗺️", "📜", "🎯", "⚔️", "🛡️", "🏹", "🗡️", "🎪", "🎭", "🎨"
        ],
        "buff": [
            "💫", "✨", "🌟", "🔮", "🌙", "⚡", "🔥", "💎", "🌊", "🍃"
        ]
    }

    available_assets = assets.get(asset_type, assets["general"])
    return random.choice(available_assets)

def get_anime_icon_url(filename: str) -> str:
    """Get URL for anime icon that Discord can access"""
    try:
        # Convert .ico to .PNG for web compatibility
        if filename.endswith('.ico'):
            filename = filename.replace('.ico', '.PNG')
        
        # Use direct GitHub raw URLs or your deployed static server
        import urllib.parse
        encoded_filename = urllib.parse.quote(filename)
        
        # Try a few different anime icon sources
        possible_urls = [
            f"https://raw.githubusercontent.com/microsoft/vscode-icons/main/icons/{encoded_filename}",
            f"https://cdn.jsdelivr.net/gh/microsoft/vscode-icons@main/icons/{encoded_filename}",
            # Fallback to a placeholder if needed
            "https://via.placeholder.com/64x64/7289da/ffffff?text=🌟"
        ]
        
        # For now, return a placeholder since we don't have a working static server
        return "https://via.placeholder.com/64x64/7289da/ffffff?text=🌟"
        
    except Exception as e:
        print(f"Error generating anime icon URL: {e}")
        return ""

def get_random_anime_icon() -> str:
    """Get a random anime icon URL"""
    try:
        base_path = Path(__file__).parent.parent.parent / "attached_assets"
        all_icons = []

        for pack_dir in ["Token Anime Pack", "Token Anime Pack 2", "Token Anime Pack 3", "Token Anime Pack 4"]:
            png_path = base_path / pack_dir / "PNG"
            if png_path.exists():
                all_icons.extend([f.name for f in png_path.iterdir() if f.suffix.lower() == '.png'])

        if all_icons:
            import random
            selected_icon = random.choice(all_icons)
            return get_anime_icon_url(selected_icon)

        return None
    except Exception as e:
        print(f"Error getting random anime icon: {e}")
        return None

def get_level_up_icon() -> str:
    """Get a special icon for level up notifications"""
    level_up_icons = [
        "Dragon Ball Z", "Naruto", "One Piece", "Bleach", "Hunter x Hunter",
        "Full Metal Alchemist", "Code Geass", "Neon Genesis Evangelion",
        "Tengen Toppa Gurren Lagann", "Kill La Kill"
    ]

    selected_icon = random.choice(level_up_icons)
    return f"https://raw.githubusercontent.com/replit/replit/main/attached_assets/Token%20Anime%20Pack/PNG/{selected_icon}.PNG"

def get_quest_icon() -> str:
    """Get a special icon for quest notifications"""
    quest_icons = [
        "Sword Art Online", "Fairy Tail", "Shingeki no Kyojin", "Tokyo Ghoul",
        "Akagame ga Kill", "No Game No Life", "Psycho Pass", "Fate Stay Night",
        "Guilty Crown", "Log Horizon"
    ]

    selected_icon = random.choice(quest_icons)
    return f"https://raw.githubusercontent.com/replit/replit/main/attached_assets/Token%20Anime%20Pack/PNG/{selected_icon}.PNG"

def get_anime_icon_filename(theme: str = None) -> str:
    """Get a random anime icon filename based on theme"""
    base_path = Path("attached_assets")

    available_files = []

    if theme and theme in ANIME_ICON_THEMES:
        # Get specific theme
        theme_data = ANIME_ICON_THEMES[theme]
        for filename in theme_data["files"]:
            # Search through all token packs
            for pack in ["Token Anime Pack", "Token Anime Pack 2", "Token Anime Pack 3", "Token Anime Pack 4"]:
                file_path = base_path / pack / "PNG" / filename
                if file_path.exists():
                    available_files.append(filename)

    else:
        # Get random from all available
        for theme_data in ANIME_ICON_THEMES.values():
            for filename in theme_data["files"]:
                for pack in ["Token Anime Pack", "Token Anime Pack 2", "Token Anime Pack 3", "Token Anime Pack 4"]:
                    file_path = base_path / pack / "PNG" / filename
                    if file_path.exists():
                        available_files.append(filename)

    if available_files:
        return random.choice(available_files)

    return None