# Working with PostgreSQL Schemas in Supabase

This guide explains how to use custom schemas in your Supabase PostgreSQL database with FastAPI.

## What are PostgreSQL Schemas?

In PostgreSQL, a schema is a namespace that contains named database objects such as tables, views, indexes, data types, functions, and operators. Schemas help organize database objects into logical groups and allow different users to use the same database without interfering with each other.

Benefits of using schemas:
- Organize database objects into logical groups
- Avoid name conflicts between objects
- Control access permissions at the schema level
- Isolate your application's tables from other applications using the same database

## How Schemas Work in Supabase

By default, Supabase uses the `public` schema for all tables. However, you can create and use custom schemas to better organize your database.

### Schema Hierarchy in Supabase

1. `public` - The default schema where tables are created if no schema is specified
2. `auth` - Used by Supabase for authentication tables
3. `storage` - Used by Supabase for storage service
4. Your custom schemas (e.g., `wellershoff`)

## Using the Wellershoff Schema

Your FastAPI application is now configured to use the `wellershoff` schema for all database operations. Here's how it works:

1. **Schema Creation**: The schema is automatically created if it doesn't exist when your application starts
2. **Search Path**: The search path is set to `wellershoff, public` so queries look in your schema first
3. **Table Creation**: All SQLAlchemy models will create tables in the `wellershoff` schema
4. **Querying**: All queries will search the `wellershoff` schema first, then fall back to `public`

## Testing Schema Setup

To verify that the schema is working correctly, run:

```bash
python test_schema.py
```

This will:
1. Check if the `wellershoff` schema exists
2. Create tables in the schema
3. Perform CRUD operations on a test user
4. Verify all operations are happening in the correct schema

## Database Migrations with Alembic

If you're using Alembic for database migrations, you'll need to configure it to work with your schema:

1. Modify `alembic/env.py` to include schema information
2. Set the schema name in your migration scripts

Example configuration for Alembic:

```python
# In alembic/env.py
from app.db.database import SCHEMA_NAME

def run_migrations_online():
    # ...
    with connectable.connect() as connection:
        # Set search path to include your schema
        connection.execute(f"SET search_path TO {SCHEMA_NAME}, public")
        
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Add this to include the schema in migrations
            include_schemas=True,
            version_table_schema=SCHEMA_NAME
        )
        
        with context.begin_transaction():
            context.run_migrations()
```

## Manually Accessing the Schema in pgAdmin or Supabase Dashboard

To view or manage your schema in pgAdmin or the Supabase dashboard:

1. Connect to your Supabase database
2. Navigate to "Schemas" in the object browser
3. Select the `wellershoff` schema
4. You can now see all tables, views, and other objects in this schema

## Querying Specific Schemas

If you need to explicitly query tables in different schemas:

```sql
-- Query from wellershoff schema
SELECT * FROM wellershoff.users;

-- Query from public schema
SELECT * FROM public.some_table;
```

In your SQLAlchemy queries, the correct schema is used automatically based on your configuration.