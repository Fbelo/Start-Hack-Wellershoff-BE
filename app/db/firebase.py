from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Path to Firebase credentials file
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "firebase-credentials.json")

# Initialize Firebase (only once)
_firebase_app = None

def get_firebase_app():
    """
    Get or initialize the Firebase app
    """
    global _firebase_app
    if _firebase_app is None:
        try:
            _firebase_app = firebase_admin.get_app()
        except ValueError:
            # If no app exists, initialize a new one
            if os.path.exists(FIREBASE_CREDENTIALS):
                cred = credentials.Certificate(FIREBASE_CREDENTIALS)
                _firebase_app = firebase_admin.initialize_app(cred)
            else:
                # For development without credentials file, use App Engine credentials
                _firebase_app = firebase_admin.initialize_app()
    return _firebase_app

def get_firestore_db():
    """
    Get a Firestore client
    """
    app = get_firebase_app()
    return firestore.client(app)

# Define collection names as constants
COLLECTION_NEWS = "news"
COLLECTION_USERS = "users"
COLLECTION_PORTFOLIO_ASSETS = "portfolio_assets"