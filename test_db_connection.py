"""
Test script to verify database connection to Supabase
"""
import os
import sys
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Add project root to Python path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database connection
from app.db.database import engine, Base, SessionLocal, SCHEMA_NAME, create_schema_if_not_exists
from app.db.models import User
from app.api.schemas.user import UserModel

def test_database_connection():
    """Test the connection to the Supabase database"""
    print("Testing database connection...")
    
    try:
        # Print the database URL (with masked password)
        from app.db.database import DATABASE_URL
        if DATABASE_URL:
            # Mask the password in the URL for display
            parts = DATABASE_URL.split(":")
            if len(parts) >= 3:
                # Format: postgresql://user:password@host:port/dbname
                user_part = parts[1].lstrip("/")
                password_part = parts[2].split("@")[0]
                masked_url = DATABASE_URL.replace(password_part, "********")
                print(f"Using connection URL: {masked_url}")
                
                # Check if URL starts with postgresql://
                if not DATABASE_URL.startswith("postgresql://"):
                    print("⚠️  Warning: URL should start with 'postgresql://' for SQLAlchemy")
        else:
            print("⚠️  Warning: No DATABASE_URL found!")
        
        # Try to connect to the database
        connection = engine.connect()
        connection.close()
        print("✅ Successfully connected to the database!")
        return True
    except SQLAlchemyError as e:
        print(f"❌ Failed to connect to the database: {e}")
        print("\nDebug information:")
        print(f"- Database URL prefix: {DATABASE_URL.split('://')[0] if DATABASE_URL else 'None'}")
        print("- SQLAlchemy version:", sys.modules.get("sqlalchemy").__version__ if "sqlalchemy" in sys.modules else "Unknown")
        print("- Check that your connection string uses 'postgresql://' not 'postgres://'")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_create_tables():
    """Test creating tables in the database"""
    print("\nTesting table creation...")
    
    try:
        # Ensure schema exists first
        create_schema_if_not_exists()
        
        # Print schema information
        print(f"Using schema: {SCHEMA_NAME}")
        
        # Create all tables defined in the models
        Base.metadata.create_all(bind=engine)
        print("✅ Successfully created tables!")
        
        # Verify tables exist in the correct schema
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{SCHEMA_NAME}'"))
            tables = [row[0] for row in result]
            print(f"Tables in schema '{SCHEMA_NAME}': {', '.join(tables) if tables else 'None'}")
            
            if not tables:
                print("⚠️ Warning: No tables found in the schema!")
        
        return True
    except SQLAlchemyError as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def test_user_operations():
    """Test basic CRUD operations with the User model"""
    print("\nTesting user operations...")
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Print information about the schema being used
        print(f"Using schema: {SCHEMA_NAME}")
        
        # Set the search path for this session to ensure we're using the right schema
        from sqlalchemy import text
        db.execute(text(f"SET search_path TO {SCHEMA_NAME}, public"))
        
        # Create a test user
        test_user = User(
            name="Test User",
            email="test@example.com",
            profile_picture="https://example.com/test.jpg",
            preferences={"test_preference": True}
        )
        
        # Add the user to the session
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Successfully created test user with ID: {test_user.id}")
        
        # Query the user
        queried_user = db.query(User).filter(User.email == "test@example.com").first()
        if queried_user:
            print(f"✅ Successfully queried test user: {queried_user.name}")
        else:
            print("❌ Failed to query test user")
            return False
        
        # Update the user
        queried_user.name = "Updated Test User"
        db.commit()
        db.refresh(queried_user)
        print(f"✅ Successfully updated test user: {queried_user.name}")
        
        # Delete the user
        db.delete(queried_user)
        db.commit()
        print("✅ Successfully deleted test user")
        
        # Verify deletion
        deleted_user = db.query(User).filter(User.email == "test@example.com").first()
        if not deleted_user:
            print("✅ Confirmed test user was deleted")
        else:
            print("❌ Failed to delete test user")
            return False
        
        return True
    
    except SQLAlchemyError as e:
        print(f"❌ Failed during user operations: {e}")
        return False
    finally:
        db.close()

def main():
    """Main function to run all tests"""
    print("=== Supabase Database Connection Test ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Get connection string and mask password for display
    connection_url = os.getenv("POSTGRES_URL", "")
    masked_url = ""
    if connection_url:
        parts = connection_url.split(":")
        if len(parts) >= 3:
            # Format: postgres://user:password@host:port/dbname
            user_part = parts[1].lstrip("/")
            password_part = parts[2].split("@")[0]
            masked_url = connection_url.replace(password_part, "********")
        
        # Check for potential dialect issue
        if connection_url.startswith("postgres://"):
            print("⚠️  WARNING: Your connection URL starts with 'postgres://' but SQLAlchemy requires 'postgresql://'")
            print("   The code should automatically fix this, but keep it in mind if issues persist.")
    
    # Print database connection details
    print("Database connection details:")
    print(f"Connection URL (masked): {masked_url}")
    print(f"Host: {os.getenv('POSTGRES_HOST')}")
    print(f"Port: {os.getenv('POSTGRES_PORT', '5432')}")
    print(f"Database: {os.getenv('POSTGRES_DB_NAME')}")
    print(f"User: {os.getenv('POSTGRES_USER')}")
    print(f"Schema: {SCHEMA_NAME}")
    print("\n")
    
    # Ensure schema exists before running tests
    print(f"Checking for schema '{SCHEMA_NAME}'...")
    schema_exists = create_schema_if_not_exists()
    
    # Run tests
    connection_result = test_database_connection()
    
    if connection_result:
        tables_result = test_create_tables()
        
        if tables_result:
            user_ops_result = test_user_operations()
    
    print("\n=== Test Summary ===")
    if connection_result:
        print("✅ Database connection successful")
        
        if tables_result:
            print("✅ Table creation successful")
            
            if user_ops_result:
                print("✅ User operations successful")
                print("\n🎉 All tests passed! Your Supabase connection is working correctly.")
            else:
                print("❌ User operations failed")
        else:
            print("❌ Table creation failed")
    else:
        print("❌ Database connection failed")
        print("\nCommon issues and solutions:")
        print("1. NoSuchModuleError for postgres dialect: Change 'postgres://' to 'postgresql://' in your connection URL")
        print("2. Check if the connection URL in .env is correct")
        print("3. Make sure you're using the pooler URL from Supabase (aws-*.pooler.supabase.com)")
        print("4. Verify that your IP address is allowed in Supabase's database settings")
        print("5. Ensure SSL is enabled for the connection")

if __name__ == "__main__":
    main()