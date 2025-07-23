# Database Scripts

This directory contains scripts for managing the GateGrind V2 database.

## Scripts Overview

### `init_db.py` - Database Initialization Script

Complete database initialization script that handles migrations, seeding, and verification.

**Usage:**
```bash
# Full initialization (migrations + seeding + verification)
python scripts/init_db.py

# Force re-initialization (WARNING: drops existing data)
python scripts/init_db.py --force

# Only run migrations
python scripts/init_db.py --migrate-only

# Only run seeding
python scripts/init_db.py --seed-only

# Show help
python scripts/init_db.py --help
```

**Features:**
- ✅ Runs Alembic migrations to create V2 schema
- ✅ Seeds database with movement categories, skill trees, and movements
- ✅ Verifies database setup and data integrity
- ✅ Idempotent operations (safe to run multiple times)
- ✅ Production-safe with proper error handling

### `seed.py` - Database Seeding Script

Standalone seeding script that populates the database with initial data from `refactor.md`.

**Usage:**
```bash
python scripts/seed.py
```

**Data Sources:**
- Movement Categories: `refactor.md` lines 131-149 (MOVEMENT_CATEGORIES_SEED)
- Skill Tree Library: `refactor.md` lines 151-270 (SKILL_TREE_LIBRARY)

### `smoke_orm.py` - ORM Testing Script

Testing script for validating SQLAlchemy ORM functionality.

## Database Setup Process

For a fresh database setup, follow these steps:

1. **Ensure environment variables are set:**
   ```bash
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

2. **Run the initialization script:**
   ```bash
   python scripts/init_db.py
   ```

3. **Verify the setup:**
   The script will automatically verify that:
   - All V2 tables are created
   - 18 movement categories are seeded
   - 90 skill tree nodes are created
   - 149 movements are populated

## Troubleshooting

### Common Issues

**Import Errors:**
- Ensure you're running from the project root directory
- Check that all dependencies are installed

**Database Connection Errors:**
- Verify `DATABASE_URL` environment variable is set correctly
- Ensure database server is running and accessible

**Migration Errors:**
- Check Alembic configuration in `alembic.ini`
- Verify database permissions

### Getting Help

Run any script with `--help` to see available options:
```bash
python scripts/init_db.py --help
```

## Development Notes

- All scripts are designed to be idempotent (safe to run multiple times)
- Scripts follow the project's engineering standards from `project_rules.md`
- Data strictly follows specifications from `refactor.md`
- No business logic is implemented in scripts (API-first approach)