"""
Test script to verify schema creation and usage with Supabase
"""
import os
import sys
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to Python path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database connection
from app.db.database import engine, Base, SessionLocal, SCHEMA_NAME
from app.models.user import User

def test_schema_creation():
    """Test that the schema exists and is being used"""
    print(f"Testing schema '{SCHEMA_NAME}' exists...")
    
    try:
        with engine.connect() as connection:
            # Check if schema exists
            query = text(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{SCHEMA_NAME}'")
            result = connection.execute(query)
            schema_exists = result.fetchone() is not None
            
            if schema_exists:
                print(f"✅ Schema '{SCHEMA_NAME}' exists!")
            else:
                print(f"❌ Schema '{SCHEMA_NAME}' does not exist!")
                return False
            
            # Check if the search path includes our schema
            result = connection.execute(text("SHOW search_path"))
            search_path = result.fetchone()[0]
            print(f"Current search path: {search_path}")
            
            if SCHEMA_NAME in search_path:
                print(f"✅ Schema '{SCHEMA_NAME}' is in the search path!")
            else:
                print(f"❌ Schema '{SCHEMA_NAME}' is not in the search path!")
                return False
                
            return True
    except SQLAlchemyError as e:
        print(f"❌ Error checking schema: {e}")
        return False

def test_table_creation():
    """Test creating tables in the specified schema"""
    print(f"\nTesting table creation in schema '{SCHEMA_NAME}'...")
    
    try:
        # Create all tables defined in the models
        Base.metadata.create_all(bind=engine)
        print(f"✅ Tables created in schema '{SCHEMA_NAME}'!")
        
        # Verify the tables were created in the correct schema
        with engine.connect() as connection:
            query = text(f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = '{SCHEMA_NAME}' 
                AND table_type = 'BASE TABLE'
            """)
            result = connection.execute(query)
            tables = result.fetchall()
            
            if tables:
                print(f"Tables in schema '{SCHEMA_NAME}':")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print(f"❌ No tables found in schema '{SCHEMA_NAME}'!")
                return False
                
            return True
    except SQLAlchemyError as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def test_user_operations():
    """Test basic CRUD operations with the User model in the specified schema"""
    print(f"\nTesting user operations in schema '{SCHEMA_NAME}'...")
    
    # Create a session
    db = SessionLocal()
    
    try:
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
        
        # Verify the user is in the correct schema
        with engine.connect() as connection:
            query = text(f"""
                SELECT table_schema 
                FROM information_schema.tables 
                WHERE table_name = 'users'
            """)
            result = connection.execute(query)
            schemas = result.fetchall()
            print(f"The 'users' table exists in schemas: {[schema[0] for schema in schemas]}")
        
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
    print("=== Supabase Schema Test ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Run tests
    schema_result = test_schema_creation()
    
    if schema_result:
        tables_result = test_table_creation()
        
        if tables_result:
            user_ops_result = test_user_operations()
    
    print("\n=== Test Summary ===")
    if schema_result:
        print(f"✅ Schema '{SCHEMA_NAME}' exists and is in the search path")
        
        if tables_result:
            print(f"✅ Tables created in schema '{SCHEMA_NAME}'")
            
            if user_ops_result:
                print("✅ User operations successful")
                print(f"\n🎉 All tests passed! Your Supabase connection is working correctly with schema '{SCHEMA_NAME}'.")
            else:
                print("❌ User operations failed")
        else:
            print(f"❌ Table creation in schema '{SCHEMA_NAME}' failed")
    else:
        print(f"❌ Schema '{SCHEMA_NAME}' setup failed")

if __name__ == "__main__":
    main()