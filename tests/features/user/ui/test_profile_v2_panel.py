"""Tests for the V2 Profile Panel"""
import pytest
import discord
from unittest.mock import MagicMock, AsyncMock, patch
from features.user.ui.profile_v2_panel import ProfileV2Panel, ProfileV2View, build_profile_v2_embed


@pytest.fixture
def mock_user():
    """Create a mock Discord user"""
    user = MagicMock(spec=discord.User)
    user.id = 123456789
    user.display_name = "TestUser"
    user.name = "testuser"
    return user


@pytest.fixture
def mock_bot():
    """Create a mock bot"""
    return MagicMock()


@pytest.fixture
def mock_profile_data():
    """Mock V2 profile API response"""
    return {
        "id": 1,
        "discord_id": "123456789",
        "username": "TestUser",
        "level": 10,
        "xp": 500,
        "xp_to_next_level": 1000,
        "aura": 150,
        "stats": {
            "strength": {
                "level": 5,
                "xp": 200,
                "xp_to_next_level": 400,
                "total_xp": 1200
            },
            "endurance": {
                "level": 4,
                "xp": 150,
                "xp_to_next_level": 300,
                "total_xp": 900
            },
            "technique": {
                "level": 3,
                "xp": 100,
                "xp_to_next_level": 250,
                "total_xp": 600
            }
        },
        "dungeon_progress": {
            "current_tier": "Shadow",
            "current_level": 5,
            "best_level": 7,
            "total_trials_completed": 25
        },
        "dungeon_keys": [
            {"tier": "Shadow", "quantity": 3}
        ],
        "unlocked_skills": [
            {"id": 1, "name": "Power Strike", "category": "Strength"},
            {"id": 2, "name": "Iron Will", "category": "Endurance"}
        ],
        "active_quests": [
            {"id": 1, "name": "Daily Training", "quest_type": "daily", "completed": False}
        ]
    }


class TestProfileV2Panel:
    """Test the ProfileV2Panel class"""
    
    def test_panel_registration(self):
        """Test that the panel is properly registered"""
        assert ProfileV2Panel.key == "profile_v2"
        assert ProfileV2Panel.label == "Profile V2"
        assert ProfileV2Panel.emoji == "⚡"
    
    @pytest.mark.asyncio
    async def test_render_embed_success(self, mock_bot, mock_user, mock_profile_data):
        """Test successful embed rendering"""
        with patch('features.user.ui.profile_v2_panel.APIClient') as mock_api_class:
            mock_api = mock_api_class.return_value
            mock_api.get_user_profile_v2 = AsyncMock(return_value=mock_profile_data)
            
            embed = await ProfileV2Panel.render_embed(mock_bot, mock_user)
            
            assert isinstance(embed, discord.Embed)
            assert embed.color.value == 0x9146FF  # Purple color
            assert "Ascendant Profile V2" in embed.description
            assert "TestUser" in embed.description
            assert "Level 10" in embed.description
            assert "Aura: 150" in embed.description
    
    @pytest.mark.asyncio
    async def test_render_embed_api_failure(self, mock_bot, mock_user):
        """Test embed rendering when API fails"""
        with patch('features.user.ui.profile_v2_panel.APIClient') as mock_api_class:
            mock_api = mock_api_class.return_value
            mock_api.get_user_profile_v2 = AsyncMock(side_effect=Exception("API Error"))
            
            embed = await ProfileV2Panel.render_embed(mock_bot, mock_user)
            
            assert isinstance(embed, discord.Embed)
            assert embed.color == discord.Color.red()
            assert "System Alert" in embed.description
            assert "OFFLINE" in embed.description
    
    @pytest.mark.asyncio
    async def test_build_view(self, mock_bot, mock_user):
        """Test view building"""
        view = await ProfileV2Panel.build_view(mock_bot, mock_user)
        
        assert isinstance(view, ProfileV2View)
        assert view.timeout == 300
        # Should have dropdown + 4 action buttons
        assert len(view.children) >= 5


class TestProfileV2View:
    """Test the ProfileV2View class"""
    
    def test_view_initialization(self, mock_bot, mock_user):
        """Test view initialization"""
        view = ProfileV2View(mock_bot, mock_user)
        
        assert view.timeout == 300
        assert view.bot == mock_bot
        assert view.user == mock_user
        # Check that buttons are added
        button_labels = [child.label for child in view.children if hasattr(child, 'label')]
        assert "📊 Detailed Stats" in button_labels
        assert "🌟 Skills" in button_labels
        assert "🏰 Dungeons" in button_labels
        assert "⚔️ Quests" in button_labels


@pytest.mark.asyncio
async def test_build_profile_v2_embed(mock_bot, mock_user, mock_profile_data):
    """Test the build_profile_v2_embed function"""
    with patch('features.user.ui.profile_v2_panel.APIClient') as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.get_user_profile_v2 = AsyncMock(return_value=mock_profile_data)
        
        embed = await build_profile_v2_embed(mock_bot, mock_user)
        
        assert isinstance(embed, discord.Embed)
        # Check that all key data is included
        assert "Level 10" in embed.description
        assert "500" in embed.description  # Current XP
        assert "1000" in embed.description  # XP to next level
        assert "Strength: Lv.5" in embed.description
        assert "Skills Unlocked: 2" in embed.description
        assert "Shadow Tier" in embed.description