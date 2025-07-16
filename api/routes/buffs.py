from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
import asyncpg

from api.models.buff import BuffInventory, ActiveBuff
from api.models.common import SuccessResponse
from api.dependencies import get_db_pool, get_current_user, is_development_mode

router = APIRouter()

def get_mock_buff_inventory() -> BuffInventory:
    """Get mock buff inventory for development mode"""
    from datetime import datetime, timedelta
    
    mock_active_buffs = [
        ActiveBuff(
            buff_id=1,
            name="Shadow Focus",
            description="Increased XP gain for 2 hours",
            effects={"xp_multiplier": 1.5},
            stacks=1,
            expires_at=datetime.now() + timedelta(hours=1, minutes=30),
            time_remaining=90
        ),
        ActiveBuff(
            buff_id=2,
            name="Iron Will",
            description="Reduced cooldowns for 1 hour",
            effects={"cooldown_reduction": 0.5},
            stacks=1,
            expires_at=datetime.now() + timedelta(minutes=45),
            time_remaining=45
        )
    ]
    
    return BuffInventory(
        consumable_buffs=[],
        active_buffs=mock_active_buffs,
        total_active_effects={
            "xp_multiplier": 1.5,
            "cooldown_reduction": 0.5
        }
    )

def get_mock_consumable_inventory() -> Dict[str, int]:
    """Get mock consumable buff inventory"""
    return {
        "void_crystal": 2,
        "time_rift": 1,
        "shadow_essence": 3
    }

@router.get("/inventory", response_model=BuffInventory)
async def get_buff_inventory(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool)
):
    """Get user's buff inventory (active buffs and consumables)"""
    # Development mode: return mock data
    if is_development_mode() or db_pool is None:
        return get_mock_buff_inventory()
    
    # Production mode: use buff engine
    try:
        user_id = current_user["user_id"]
        
        # Import buff engine functions
        from features.buffs.logic.engine import get_active_buffs
        from features.user.logic.user_data import load_user_data
        
        # Get user data and active buffs
        user_data = await load_user_data(user_id)
        active_buffs_data = await get_active_buffs(user_id, user_data)
        
        # Convert to API format
        active_buffs = []
        total_effects = {}
        
        for buff_data in active_buffs_data:
            active_buff = ActiveBuff(
                buff_id=hash(buff_data.get("buff_id", "unknown")),  # Convert string to int
                name=buff_data.get("name", "Unknown Buff"),
                description=buff_data.get("description", ""),
                effects=buff_data.get("effects", {}),
                stacks=1,
                expires_at=buff_data.get("end_time"),
                time_remaining=int(buff_data.get("remaining_hours", 0) * 60)
            )
            active_buffs.append(active_buff)
            
            # Aggregate effects
            for effect, value in buff_data.get("effects", {}).items():
                if effect in total_effects:
                    if effect == "xp_multiplier":
                        total_effects[effect] *= value
                    else:
                        total_effects[effect] += value
                else:
                    total_effects[effect] = value
        
        return BuffInventory(
            consumable_buffs=[],  # TODO: Convert consumable inventory
            active_buffs=active_buffs,
            total_active_effects=total_effects
        )
        
    except Exception as e:
        print(f"[ERROR] Failed to get buff inventory: {e}")
        raise HTTPException(status_code=500, detail="Failed to get buff inventory")

@router.get("/consumables", response_model=Dict[str, int])
async def get_consumable_inventory(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool)
):
    """Get user's consumable buff inventory"""
    # Development mode: return mock data
    if is_development_mode() or db_pool is None:
        return get_mock_consumable_inventory()
    
    # Production mode: get from user data
    try:
        user_id = current_user["user_id"]
        from features.user.logic.user_data import load_user_data
        
        user_data = await load_user_data(user_id)
        inventory = user_data.get("buff_inventory", {})
        
        return inventory
        
    except Exception as e:
        print(f"[ERROR] Failed to get consumable inventory: {e}")
        return {}

@router.post("/consumables/{buff_id}/use", response_model=SuccessResponse)
async def use_consumable_buff(
    buff_id: str,
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool)
):
    """Use a consumable buff from inventory"""
    # Development mode: return mock success
    if is_development_mode() or db_pool is None:
        return SuccessResponse(
            message=f"Used {buff_id} successfully! (development mode)",
            data={
                "buff_id": buff_id,
                "user_id": current_user["user_id"],
                "effects_applied": {"instant_xp": 100},
                "mode": "development"
            }
        )
    
    # Production mode: use buff engine
    try:
        user_id = current_user["user_id"]
        
        # Import buff engine
        from features.buffs.logic.engine import use_consumable_buff
        
        # Create a mock bot object
        class MockBot:
            def __init__(self, db_pool):
                self.db_pool = db_pool
        
        bot = MockBot(db_pool)
        result = await use_consumable_buff(bot, user_id, buff_id)
        
        if result["success"]:
            return SuccessResponse(
                message=f"Used {result['buff']['name']} successfully!",
                data={
                    "buff_id": buff_id,
                    "user_id": user_id,
                    "buff_type": result["type"],
                    "effects_applied": result["buff"]["effects"],
                    "mode": "production"
                }
            )
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to use buff"))
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to use consumable buff: {e}")
        raise HTTPException(status_code=500, detail="Failed to use consumable buff")

@router.post("/apply/{buff_id}", response_model=SuccessResponse)
async def apply_buff(
    buff_id: str,
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool)
):
    """Apply a buff to the user (admin/testing endpoint)"""
    # Development mode: return mock success
    if is_development_mode() or db_pool is None:
        return SuccessResponse(
            message=f"Applied {buff_id} successfully! (development mode)",
            data={
                "buff_id": buff_id,
                "user_id": current_user["user_id"],
                "buff_type": "active",
                "mode": "development"
            }
        )
    
    # Production mode: use buff engine
    try:
        user_id = current_user["user_id"]
        
        # Import buff engine
        from features.buffs.logic.engine import apply_buff
        
        # Create a mock bot object
        class MockBot:
            def __init__(self, db_pool):
                self.db_pool = db_pool
        
        bot = MockBot(db_pool)
        result = await apply_buff(bot, user_id, buff_id)
        
        if result["success"]:
            return SuccessResponse(
                message=f"Applied {result['buff']['name']} successfully!",
                data={
                    "buff_id": buff_id,
                    "user_id": user_id,
                    "buff_type": result["type"],
                    "buff_name": result["buff"]["name"],
                    "effects": result["buff"]["effects"],
                    "mode": "production"
                }
            )
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to apply buff"))
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to apply buff: {e}")
        raise HTTPException(status_code=500, detail="Failed to apply buff")

@router.post("/consumables/{buff_id}/add", response_model=SuccessResponse)
async def add_consumable_buff(
    buff_id: str,
    quantity: int = 1,
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool)
):
    """Add consumable buffs to user's inventory (admin/testing endpoint)"""
    # Development mode: return mock success
    if is_development_mode() or db_pool is None:
        return SuccessResponse(
            message=f"Added {quantity}x {buff_id} to inventory! (development mode)",
            data={
                "buff_id": buff_id,
                "quantity": quantity,
                "user_id": current_user["user_id"],
                "mode": "development"
            }
        )
    
    # Production mode: use buff engine
    try:
        user_id = current_user["user_id"]
        
        # Import buff engine
        from features.buffs.logic.engine import add_consumable_buff
        
        success = await add_consumable_buff(user_id, buff_id, quantity)
        
        if success:
            # Get buff name from definitions
            from core.config import BUFF_DEFINITIONS
            buff_def = BUFF_DEFINITIONS.get(buff_id, {})
            buff_name = buff_def.get("name", buff_id)
            
            return SuccessResponse(
                message=f"Added {quantity}x {buff_name} to inventory!",
                data={
                    "buff_id": buff_id,
                    "quantity": quantity,
                    "user_id": user_id,
                    "buff_name": buff_name,
                    "mode": "production"
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid consumable buff ID")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to add consumable buff: {e}")
        raise HTTPException(status_code=500, detail="Failed to add consumable buff")

@router.post("/random", response_model=SuccessResponse)
async def grant_random_buff(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool)
):
    """Grant a random buff to the user (admin/testing endpoint)"""
    # Development mode: return mock success
    if is_development_mode() or db_pool is None:
        import random
        rarities = ["common", "uncommon", "rare", "legendary"]
        rarity = random.choice(rarities)
        
        return SuccessResponse(
            message=f"Granted random {rarity} buff! (development mode)",
            data={
                "rarity": rarity,
                "buff_name": f"Mock {rarity.title()} Buff",
                "user_id": current_user["user_id"],
                "mode": "development"
            }
        )
    
    # Production mode: use buff engine
    try:
        user_id = current_user["user_id"]
        
        # Import buff engine
        from features.buffs.logic.engine import grant_random_buff
        
        # Create a mock bot object
        class MockBot:
            def __init__(self, db_pool):
                self.db_pool = db_pool
        
        bot = MockBot(db_pool)
        result = grant_random_buff(bot, user_id)
        
        if result:
            return SuccessResponse(
                message=f"Granted random {result['rarity']} buff: {result['buff']['name']}!",
                data={
                    "buff_id": result["buff_id"],
                    "rarity": result["rarity"],
                    "buff_name": result["buff"]["name"],
                    "user_id": user_id,
                    "mode": "production"
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate random buff")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to grant random buff: {e}")
        raise HTTPException(status_code=500, detail="Failed to grant random buff")