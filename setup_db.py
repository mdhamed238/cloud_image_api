from app.db.base import Base
from app.db.models import User, Image, Transformation
from app.db.session import engine
from dotenv import load_dotenv
import os

# Load environment variables from .env.local
dotenv_path = os.path.join(os.path.dirname(__file__), '.env.local')
load_dotenv(dotenv_path)

def setup_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    setup_db()
