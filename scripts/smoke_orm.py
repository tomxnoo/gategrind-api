"""
Full SQLAlchemy ORM + DB smoke test for GateGrind V2 models.

Validates:
1. Imports & settings load.
2. DB URL normalization for asyncpg (drops channel_binding, swaps driver prefix).
3. SQLAlchemy mappers configure cleanly (no stray MovementCategory.movements).
4. Async DB connection to Neon works.
5. Simple SELECT loads MovementCategory rows (0+ ok; confirms schema linkage).
6. Optional: load Node + Movement counts per category.

Safe to run repeatedly; read‑only.
"""

import os
import sys
import asyncio
import traceback
import urllib.parse

# --- Python path bootstrap -------------------------------------------------
sys.path.insert(0, os.path.abspath("."))

# --- Imports ---------------------------------------------------------------
try:
    from core.config import get_settings
    from core.database.models.v2 import MovementCategory, SkillTreeNode, Movement
except Exception as import_err:  # pragma: no cover
    print("IMPORT ERROR:", import_err)
    traceback.print_exc()
    raise

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func


# --- URL normalization -----------------------------------------------------
def normalize_db_url(url: str) -> str:
    """Convert sync postgres URLs to asyncpg URLs & strip problematic params."""
    # Driver swap
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)

    # Strip params asyncpg chokes on (channel_binding commonly)
    parsed = urllib.parse.urlsplit(url)
    if parsed.query:
        q = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        filtered = [(k, v) for (k, v) in q if k.lower() not in ("channel_binding",)]
        new_query = urllib.parse.urlencode(filtered)
        url = urllib.parse.urlunsplit(parsed._replace(query=new_query))
    return url


# --- Relationship introspection helper -------------------------------------
def print_relationships():
    print("\n=== Mapper Relationship Inspection ===")
    for rel in MovementCategory.__mapper__.relationships:
        print("MovementCategory ->", rel.key, "target:", rel.mapper.class_.__name__)
    for rel in SkillTreeNode.__mapper__.relationships:
        print("SkillTreeNode     ->", rel.key, "target:", rel.mapper.class_.__name__)
    for rel in Movement.__mapper__.relationships:
        print("Movement          ->", rel.key, "target:", rel.mapper.class_.__name__)
    print("=== End Relationships ===\n")


# --- Main async ------------------------------------------------------------
async def main():
    print(">>> smoke_orm: starting full ORM/DB test")
    settings = get_settings()

    raw_url = settings.DATABASE_URL
    norm_url = normalize_db_url(raw_url)

    print("RAW URL :", raw_url)
    print("NORM URL:", norm_url)

    # Neon includes sslmode=require in the URL; that typically suffices.
    engine = create_async_engine(norm_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    print_relationships()

    try:
        async with async_session() as session:
            # Force mapper config via a trivial select
            print("Running SELECT MovementCategory...")
            res = await session.execute(select(MovementCategory))
            cats = res.scalars().all()
            print(f"Loaded MovementCategory rows = {len(cats)}")
            for c in cats:
                print(f" - {c.id} ({c.name}) primary={c.primary_stat}")

            # Show counts of nodes & movements (if tables populated)
            print("\nCounting SkillTreeNode rows...")
            count_nodes = await session.scalar(select(func.count()).select_from(SkillTreeNode))
            print("SkillTreeNode count:", count_nodes)

            print("Counting Movement rows...")
            count_moves = await session.scalar(select(func.count()).select_from(Movement))
            print("Movement count:", count_moves)

            # Optional: per‑category summary if data exists
            if cats:
                print("\nPer‑category node counts:")
                stmt = (
                    select(SkillTreeNode.category_id, func.count())
                    .group_by(SkillTreeNode.category_id)
                    .order_by(SkillTreeNode.category_id)
                )
                res = await session.execute(stmt)
                for cid, ncount in res.all():
                    print(f"   {cid}: {ncount} nodes")

    except Exception as e:  # pragma: no cover
        print("\nDB TEST FAILED:", e)
        traceback.print_exc()
    finally:
        await engine.dispose()
        print(">>> smoke_orm: done.")


if __name__ == "__main__":
    asyncio.run(main())
