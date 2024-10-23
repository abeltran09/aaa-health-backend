from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

load_dotenv()

# Fetch environment variables
DATABASE_USER = os.getenv("POSTGRES_USER")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DATABASE_DB = os.getenv("POSTGRES_DB")
DATABASE_HOST = os.getenv("POSTGRES_HOST")
DATABASE_PORT = os.getenv("POSTGRES_PORT")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(" Starting the database connection process...")
try:
    
    # GET THE CONNECTION OBJECT (ENGINE) FOR THE DATABASE
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    logger.info(
        f" Connection to the {DATABASE_HOST} for user {DATABASE_USER} created successfully.")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()
except Exception as ex:
    logger.info(" Connection could not be made due to the following error: \n", ex)

