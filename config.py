import os
from dotenv import load_dotenv

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine



# Load environment variables from .env file
load_dotenv()

# Fetch DATABASE_URL from environment
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables")

#Creates the Engine that manages DB connections and dialect behaviour.
engine=create_engine(SQLALCHEMY_DATABASE_URL)
#produces a Session object (a unit-of-work you use to add/query objects)
sessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

#This function creates a DB session and yields it, then ensures cleanup by closing the session when the caller is done.
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


