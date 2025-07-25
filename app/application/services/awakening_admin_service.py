"""
Admin Service for Manual Awakening System Management

This service provides administrative functions for managing the awakening system,
including manual resets, user progress adjustments, and system monitoring.
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.infrastructure.database.models.v2.awakening import (
    AwakeningSession, AwakeningQuest, AwakeningReward, UserAwakeningProgress
)
from app.infrastructure.database.models.v2.user import User
from app.application.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class AwakeningAdminService:
    """Administrative service for awakening system management"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.cache_service = cache_service
    
    async def manual_reset_user_session(
        self, 
        user_id: int, 
        admin_id: int, 
        reason: str = "Manual admin reset"
    ) -> Dict[str, Any]:
        """
        Manually reset a user's daily session (admin function)
        
        Args:
            user_id: User ID to reset
            admin_id: Admin performing the reset
            reason: Reason for the reset
            
        Returns:
            Reset confirmation data
        """
        try:
            # Verify admin permissions (implement based on your auth system)
            admin_user = self.db.query(User).filter(User.id == admin_id).first()
            if not admin_user:
                raise ValueError("Admin user not found")
            
            # Get today's session
            today = date.today()
            session = self.db.query(AwakeningSession).filter(
                and_(
                    AwakeningSession.user_id == user_id,
                    func.date(AwakeningSession.created_at) == today
                )
            ).first()
            
            if not session:
                raise ValueError(f"No active session found for user {user_id} today")
            
            # Reset all quests in the session
            quests = self.db.query(AwakeningQuest).filter(
                AwakeningQuest.session_id == session.id
            ).all()
            
            for quest in quests:
                quest.is_completed = False
                quest.completed_at = None
                quest.current_progress = 0
            
            # Reset session
            session.completed_quests = 0
            session.is_completed = False
            session.completed_at = None
            
            # Log the admin action
            logger.warning(
                f"Manual reset performed by admin {admin_id} for user {user_id}. "
                f"Reason: {reason}"
            )
            
            self.db.commit()
            
            # Invalidate cache
            await self.cache_service.invalidate_user_cache(user_id)
            
            return {
                'user_id': user_id,
                'session_id': session.id,
                'reset_by': admin_id,
                'reset_at': datetime.utcnow().isoformat(),
                'reason': reason,
                'quests_reset': len(quests)
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error in manual reset for user {user_id}: {str(e)}")
            raise
    
    async def adjust_user_progress(
        self, 
        user_id: int, 
        admin_id: int, 
        adjustments: Dict[str, int],
        reason: str = "Manual admin adjustment"
    ) -> Dict[str, Any]:
        """
        Manually adjust user's awakening progress (admin function)
        
        Args:
            user_id: User ID to adjust
            admin_id: Admin performing the adjustment
            adjustments: Dict with fields to adjust (e.g., {'current_streak': 5})
            reason: Reason for the adjustment
            
        Returns:
            Updated progress data
        """
        try:
            # Get user progress
            user_progress = self.db.query(UserAwakeningProgress).filter(
                UserAwakeningProgress.user_id == user_id
            ).first()
            
            if not user_progress:
                raise ValueError(f"No progress record found for user {user_id}")
            
            # Apply adjustments
            old_values = {}
            for field, value in adjustments.items():
                if hasattr(user_progress, field):
                    old_values[field] = getattr(user_progress, field)
                    setattr(user_progress, field, value)
                else:
                    raise ValueError(f"Invalid field: {field}")
            
            # Log the admin action
            logger.warning(
                f"Manual progress adjustment by admin {admin_id} for user {user_id}. "
                f"Changes: {old_values} -> {adjustments}. Reason: {reason}"
            )
            
            self.db.commit()
            
            # Invalidate cache
            await self.cache_service.invalidate_user_cache(user_id)
            
            return {
                'user_id': user_id,
                'adjusted_by': admin_id,
                'adjusted_at': datetime.utcnow().isoformat(),
                'old_values': old_values,
                'new_values': adjustments,
                'reason': reason
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adjusting progress for user {user_id}: {str(e)}")
            raise
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Get awakening system statistics for monitoring
        
        Returns:
            System statistics
        """
        try:
            today = date.today()
            yesterday = today - timedelta(days=1)
            week_ago = today - timedelta(days=7)
            
            # Daily stats
            today_sessions = self.db.query(AwakeningSession).filter(
                func.date(AwakeningSession.created_at) == today
            ).count()
            
            today_completed = self.db.query(AwakeningSession).filter(
                and_(
                    func.date(AwakeningSession.created_at) == today,
                    AwakeningSession.is_completed == True
                )
            ).count()
            
            # Weekly stats
            week_sessions = self.db.query(AwakeningSession).filter(
                AwakeningSession.created_at >= week_ago
            ).count()
            
            week_completed = self.db.query(AwakeningSession).filter(
                and_(
                    AwakeningSession.created_at >= week_ago,
                    AwakeningSession.is_completed == True
                )
            ).count()
            
            # User engagement
            active_users_today = self.db.query(AwakeningSession.user_id).filter(
                func.date(AwakeningSession.created_at) == today
            ).distinct().count()
            
            active_users_week = self.db.query(AwakeningSession.user_id).filter(
                AwakeningSession.created_at >= week_ago
            ).distinct().count()
            
            # Top streaks
            top_streaks = self.db.query(UserAwakeningProgress).order_by(
                desc(UserAwakeningProgress.current_streak)
            ).limit(10).all()
            
            # Cache stats
            cache_stats = await self.cache_service.get_stats()
            
            return {
                'daily_stats': {
                    'sessions_created': today_sessions,
                    'sessions_completed': today_completed,
                    'completion_rate': round((today_completed / today_sessions * 100) if today_sessions > 0 else 0, 2),
                    'active_users': active_users_today
                },
                'weekly_stats': {
                    'sessions_created': week_sessions,
                    'sessions_completed': week_completed,
                    'completion_rate': round((week_completed / week_sessions * 100) if week_sessions > 0 else 0, 2),
                    'active_users': active_users_week
                },
                'top_streaks': [
                    {
                        'user_id': progress.user_id,
                        'current_streak': progress.current_streak,
                        'longest_streak': progress.longest_streak,
                        'total_sessions': progress.total_sessions_completed
                    }
                    for progress in top_streaks
                ],
                'cache_performance': cache_stats,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            raise
    
    async def get_user_detailed_history(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get detailed user history for admin review
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Detailed user history
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get sessions
            sessions = self.db.query(AwakeningSession).filter(
                and_(
                    AwakeningSession.user_id == user_id,
                    AwakeningSession.created_at >= cutoff_date
                )
            ).order_by(desc(AwakeningSession.created_at)).all()
            
            # Get user progress
            user_progress = self.db.query(UserAwakeningProgress).filter(
                UserAwakeningProgress.user_id == user_id
            ).first()
            
            session_details = []
            for session in sessions:
                quests = self.db.query(AwakeningQuest).filter(
                    AwakeningQuest.session_id == session.id
                ).all()
                
                session_details.append({
                    'session_id': session.id,
                    'date': session.created_at.date().isoformat(),
                    'readiness_level': session.readiness_level,
                    'quest_count': session.quest_count,
                    'completed_quests': session.completed_quests,
                    'is_completed': session.is_completed,
                    'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                    'quests': [
                        {
                            'quest_id': quest.id,
                            'quest_type': quest.quest_type,
                            'target_value': quest.target_value,
                            'current_progress': quest.current_progress,
                            'is_completed': quest.is_completed,
                            'difficulty_tier': quest.difficulty_tier,
                            'rewards': {
                                'xp': quest.xp_reward,
                                'aura': quest.aura_reward,
                                'shadow_keys': quest.shadow_key_reward
                            }
                        }
                        for quest in quests
                    ]
                })
            
            return {
                'user_id': user_id,
                'period_days': days,
                'total_sessions': len(sessions),
                'completed_sessions': sum(1 for s in sessions if s.is_completed),
                'current_progress': {
                    'current_streak': user_progress.current_streak if user_progress else 0,
                    'longest_streak': user_progress.longest_streak if user_progress else 0,
                    'total_sessions_completed': user_progress.total_sessions_completed if user_progress else 0,
                    'total_quests_completed': user_progress.total_quests_completed if user_progress else 0,
                    'total_xp_earned': user_progress.total_xp_earned if user_progress else 0,
                    'total_aura_earned': user_progress.total_aura_earned if user_progress else 0,
                    'total_shadow_keys_earned': user_progress.total_shadow_keys_earned if user_progress else 0
                },
                'sessions': session_details,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting detailed history for user {user_id}: {str(e)}")
            raise
    
    async def cleanup_old_sessions(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """
        Clean up old awakening sessions (admin maintenance function)
        
        Args:
            days_to_keep: Number of days of sessions to keep
            
        Returns:
            Cleanup statistics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Get sessions to delete
            old_sessions = self.db.query(AwakeningSession).filter(
                AwakeningSession.created_at < cutoff_date
            ).all()
            
            session_count = len(old_sessions)
            quest_count = 0
            reward_count = 0
            
            # Delete associated data
            for session in old_sessions:
                # Count and delete quests
                quests = self.db.query(AwakeningQuest).filter(
                    AwakeningQuest.session_id == session.id
                ).all()
                quest_count += len(quests)
                
                for quest in quests:
                    self.db.delete(quest)
                
                # Count and delete rewards
                rewards = self.db.query(AwakeningReward).filter(
                    AwakeningReward.session_id == session.id
                ).all()
                reward_count += len(rewards)
                
                for reward in rewards:
                    self.db.delete(reward)
                
                # Delete session
                self.db.delete(session)
            
            self.db.commit()
            
            logger.info(
                f"Cleaned up {session_count} sessions, {quest_count} quests, "
                f"and {reward_count} rewards older than {days_to_keep} days"
            )
            
            return {
                'sessions_deleted': session_count,
                'quests_deleted': quest_count,
                'rewards_deleted': reward_count,
                'cutoff_date': cutoff_date.isoformat(),
                'cleaned_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during cleanup: {str(e)}")
            raise