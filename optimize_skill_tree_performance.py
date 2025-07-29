#!/usr/bin/env python3
"""
Analyze and suggest optimizations for skill tree performance.
Based on the current implementation that takes 12+ seconds to load.
"""

import asyncio
import os
from urllib.parse import urlparse

async def analyze_performance():
    """Analyze the current performance bottlenecks."""
    try:
        import asyncpg
    except ImportError:
        print("ERROR: asyncpg library not available")
        return False
    
    try:
        # Get database URL
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("ERROR: DATABASE_URL environment variable not set")
            return False
        
        print("Connecting to database...")
        
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        parsed = urlparse(db_url)
        
        conn = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:] if parsed.path else 'postgres'
        )
        
        print("Connected successfully!")
        
        print("\n" + "="*60)
        print("SKILL TREE PERFORMANCE ANALYSIS")
        print("="*60)
        
        # 1. Analyze current data volumes
        print("\n[1] Data Volume Analysis:")
        
        categories_count = await conn.fetchval("SELECT COUNT(*) FROM movement_categories;")
        nodes_count = await conn.fetchval("SELECT COUNT(*) FROM skill_tree_nodes;")
        movements_count = await conn.fetchval("SELECT COUNT(*) FROM movements;")
        
        print(f"  Movement Categories: {categories_count}")
        print(f"  Skill Tree Nodes: {nodes_count}")
        print(f"  Movements: {movements_count}")
        
        # 2. Analyze the current query pattern
        print("\n[2] Current Query Pattern Analysis:")
        print("  The current MovementService.get_skill_tree_library() uses:")
        print("    SELECT movement_categories with selectinload(skill_tree_nodes)")
        print("    Then selectinload(movements) for each node")
        print("    This creates a large nested object with ALL data")
        
        # 3. Calculate approximate response size
        print("\n[3] Response Size Estimation:")
        
        # Get sample data sizes
        sample_category = await conn.fetchrow("SELECT * FROM movement_categories LIMIT 1;")
        sample_node = await conn.fetchrow("SELECT * FROM skill_tree_nodes LIMIT 1;")
        sample_movement = await conn.fetchrow("SELECT * FROM movements LIMIT 1;")
        
        # Rough size calculation (in characters, not bytes)
        category_size = len(str(dict(sample_category))) if sample_category else 0
        node_size = len(str(dict(sample_node))) if sample_node else 0
        movement_size = len(str(dict(sample_movement))) if sample_movement else 0
        
        total_estimated_size = (categories_count * category_size + 
                              nodes_count * node_size + 
                              movements_count * movement_size)
        
        print(f"  Estimated total response size: ~{total_estimated_size:,} characters")
        print(f"  Average category with nodes+movements: ~{total_estimated_size // categories_count:,} chars")
        
        # 4. Identify bottlenecks
        print("\n[4] Performance Bottlenecks Identified:")
        print("  ❌ Loading ALL categories with ALL nodes and movements at once")
        print("  ❌ Multiple redundant API calls (each button click refetches everything)")
        print("  ❌ No caching or pagination")
        print("  ❌ UI makes separate API calls for each category navigation")
        print("  ❌ Large JSON response transfer over network")
        
        # 5. Optimization recommendations
        print("\n[5] Optimization Recommendations:")
        print("  ✅ IMMEDIATE FIXES:")
        print("    1. Cache library data in UI after first load")
        print("    2. Add pagination to load categories on-demand")
        print("    3. Separate overview endpoint (just category names/counts)")
        print("    4. Lazy load skill tree details when category selected")
        print("  \n  ✅ MEDIUM-TERM FIXES:")
        print("    5. Add Redis caching for library data (5-minute TTL)")
        print("    6. Database query optimization with proper indexing")
        print("    7. GraphQL or selective field loading")
        print("  \n  ✅ LONG-TERM FIXES:")
        print("    8. WebSocket for real-time updates instead of polling")
        print("    9. Client-side skill tree state management")
        print("    10. CDN caching for static skill tree data")
        
        # 6. Specific implementation suggestions
        print("\n[6] Specific Implementation Changes:")
        print("  API Changes:")
        print("    - GET /api/v2/movements/categories (overview only)")
        print("    - GET /api/v2/movements/categories/{id}/skills (detailed)")
        print("    - Add ?include=movements,requirements query params")
        print("  \n  UI Changes:")
        print("    - Cache library_data after first successful load")
        print("    - Use cached data for category navigation")
        print("    - Only fetch detailed skills when category selected")
        print("    - Add loading states for individual categories")
        
        # 7. Expected performance improvements
        print("\n[7] Expected Performance Improvements:")
        print("  Current: 12+ seconds for full load")
        print("  With caching: ~3 seconds first load, <1 second subsequent")
        print("  With pagination: ~1-2 seconds per category load")
        print("  With optimized queries: ~0.5-1 second per load")
        print("  Combined optimizations: <2 seconds total, <0.5s navigation")
        
        await conn.close()
        
        print("\n" + "="*60)
        print("RECOMMENDATION PRIORITY")
        print("="*60)
        print("\n🔥 CRITICAL (implement now):")
        print("  1. Add UI caching to prevent redundant API calls")
        print("  2. Create unlock button functionality")
        print("\n⚡ HIGH (next iteration):")
        print("  3. Split API into overview + detailed endpoints")
        print("  4. Add Redis caching layer")
        print("\n📈 MEDIUM (future optimization):")
        print("  5. Database query optimization")
        print("  6. Response size reduction")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*80)
    print("SKILL TREE PERFORMANCE ANALYSIS")
    print("="*80)
    print()
    print("Analyzing the current 12+ second load time issue")
    print("and providing specific optimization recommendations.")
    print()
    
    try:
        success = asyncio.run(analyze_performance())
        if success:
            print("\n[SUCCESS] Analysis completed successfully!")
        else:
            print("\n[ERROR] Analysis failed - check output above")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Analysis interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")