"""
Database connection configuration using SQLAlchemy with Supabase PostgreSQL
"""
import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy.schema import CreateSchema

# Load environment variables
load_dotenv()

# Schema name for the application
SCHEMA_NAME = "wellershoff"

# Get database connection URL from environment variables
# Use the full connection URL provided by Supabase
DATABASE_URL = os.getenv("POSTGRES_URL")
if not DATABASE_URL:
    raise ValueError("No database URL provided. Set the POSTGRES_URL environment variable.")

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using it
    pool_size=10,        # Number of connections to keep open
    max_overflow=20,     # Maximum number of connections to create above pool_size
    pool_recycle=3600,   # Recycle connections after one hour
    connect_args={"sslmode": "require"}  # Enable SSL for Supabase connection
)

# Create the schema if it doesn't exist
def create_schema_if_not_exists():
    with engine.connect() as connection:
        # Check if schema exists
        query = text(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{SCHEMA_NAME}'")
        result = connection.execute(query)
        schema_exists = result.fetchone() is not None
        
        if not schema_exists:
            print(f"Creating schema '{SCHEMA_NAME}'...")
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
            connection.commit()
            print(f"Schema '{SCHEMA_NAME}' created successfully")
        
        # Set search path for future queries
        connection.execute(text(f"SET search_path TO {SCHEMA_NAME}, public"))
        connection.commit()
        
        # Return whether schema exists
        return schema_exists

# Create the schema when the application starts
create_schema_if_not_exists()

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models with schema configuration
Base = declarative_base()

# Set the schema for all tables that inherit from Base
@event.listens_for(Base.metadata, "before_create")
def set_schema(target, connection, **kw):
    # This ensures all tables are created in the specified schema
    for table in target.tables.values():
        table.schema = SCHEMA_NAME

# When connecting, always set the search path to our schema
@event.listens_for(engine, "connect")
def set_search_path(dbapi_connection, connection_record):
    # Set search path for PostgreSQL connection
    cursor = dbapi_connection.cursor()
    cursor.execute(f"SET search_path TO {SCHEMA_NAME}, public")
    cursor.close()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
