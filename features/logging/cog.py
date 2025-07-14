import discord  # py-cord
from datetime import datetime, timedelta
from discord.ext import commands  # py-cord
from features.logging.ui.view import LogRepsPanel, render_log_complete_embed
from features.quests.logic.daily_quests.daily_quest_logic import update_quest_progress
# Change line 6 from:
# from features.quests.ui.quest_completion_ui import render_quest_completion_panel
# To:
from features.quests.ui.quest_completion_ui import render_quest_completion_panel
# (This should work once quest_completion_ui.py is fixed)
from features.user.ui.level_up_view import render_level_up_embed
from features.user.logic.user_data import load_user_data, save_user_data
from features.user.logic.xp_engine import calculate_xp_for_movement
from features.quests.ui.weekly.weekly_contract_panel import update_weekly_progress, create_weekly_contract_completion_embed

REP_CAPS = {
    "push_ups": 500,
    "pull_ups": 300,
    "squats": 400,
    "crunches": 500,
    "planks": 300,
    "knee_raises": 400,
    "shoulder_raises": 300,
    "bicep_curls": 300
}
COOLDOWN_MINUTES = 2

class MovementLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_log_reps(self, interaction: discord.Interaction, movement: str, reps: int):
        user = interaction.user
        user_id = user.id
        data = await load_user_data(user_id)

        now = datetime.utcnow()
        last_log_str = data.get("cooldowns", {}).get(movement)
        if last_log_str:
            last_time = datetime.fromisoformat(last_log_str)
            if now - last_time < timedelta(minutes=COOLDOWN_MINUTES):
                remaining = timedelta(minutes=COOLDOWN_MINUTES) - (now - last_time)
                minutes, seconds = divmod(int(remaining.total_seconds()), 60)
                return await interaction.response.send_message(
                    f"⏳ Cooldown active! Try again in {minutes}m {seconds}s.", ephemeral=True
                )

        # Defer immediately to avoid Discord timeout and allow loading UI
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        # --- RPG LOADING FEEDBACK (animated, cycles until content ready) ---
        loading = True
        import asyncio
        from shared.utils.headers import render_loading_embed
        async def animate_loading():
            dots = 1
            while loading:
                loading_embed = render_loading_embed(user, dot_count=dots)
                try:
                    await interaction.edit_original_response(embed=loading_embed, view=None)
                except Exception:
                    pass
                dots = dots % 3 + 1
                await asyncio.sleep(0.35)
        task = asyncio.create_task(animate_loading())
        try:
            # Store in both log_stats (for quest tracking) and rep_log (for UI display)
            stats = data.setdefault("log_stats", {})
            stats.setdefault(movement, 0)
            rep_log = data.setdefault("rep_log", {})
            today_str = now.strftime("%Y-%m-%d")
            movement_key = movement.lower().replace(" ","").replace("-","")
            rep_log_key = f"{movement_key}_{today_str}"
            cap = REP_CAPS.get(movement, 500)
            total_today = stats[movement]
            xp_earned = calculate_xp_for_movement(movement, reps)
            if total_today >= cap:
                xp_earned = int(xp_earned * 0.2)
            elif total_today + reps > cap:
                capped = total_today + reps - cap
                uncapped = reps - capped
                xp_uncapped = calculate_xp_for_movement(movement, uncapped)
                xp_capped = int(calculate_xp_for_movement(movement, capped) * 0.2)
                xp_earned = xp_uncapped + xp_capped
            stats[movement] += reps
            rep_log[rep_log_key] = rep_log.get(rep_log_key, 0) + reps
            data.setdefault("cooldowns", {})[movement] = now.isoformat()
            from features.user.logic.xp_engine import add_xp
            xp_result = await add_xp(user_id, xp_earned)
            completed_quests = await update_quest_progress(user_id, movement, reps)
            weekly_completed = await update_weekly_progress(user.id, self.bot, movement, reps)
            daily_quests = data.get("daily_quests", {}).get("quests")
            weekly_contracts = data.get("weekly_contracts", {}).get("contracts")
            embed, view = await render_log_complete_embed(
                user, movement, reps, xp_earned, user_data=data, daily_quests=daily_quests, weekly_contracts=weekly_contracts
            )
        finally:
            loading = False
            if task and not task.done():
                try:
                    task.cancel()
                    await asyncio.wait_for(task, timeout=0.5)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
                except Exception:
                    pass
            await asyncio.sleep(0.05)
        await save_user_data(user_id, data)
        # Write-through: Invalidate cache after DB write
        from core.redis_cache import invalidate_user_json_cache, get_or_cache_user_json_data
        await invalidate_user_json_cache(self.bot, user_id)
        await get_or_cache_user_json_data(self.bot, user_id)
        await interaction.edit_original_response(embed=embed, view=view)

        # Send level up notification if user leveled up
        if xp_result.get("leveled_up", False):
            # Use new UI embed for level up
            level_up_embed = await render_level_up_embed(self.bot, user, xp_result["new_level"])
            await interaction.followup.send(embed=level_up_embed, ephemeral=True)

        # Send quest completion notifications as follow-up ephemeral messages
        for quest in completed_quests:
            completion_embed = render_quest_completion_panel(quest, user if isinstance(user, discord.User) else user._user)
            await interaction.followup.send(embed=completion_embed, ephemeral=True)

        # Send weekly contract completion notifications as follow-up ephemeral messages
        for contract in weekly_completed:
            weekly_completion_embed = create_weekly_contract_completion_embed(contract)
            await interaction.followup.send(embed=weekly_completion_embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(MovementLogger(bot))