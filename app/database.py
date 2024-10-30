from dotenv import load_dotenv
import os
from sqlmodel import SQLModel, Session, create_engine
import logging

# Load environment variables
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

logger.info("Starting the database connection process...")

try:
    # Get the connection object (engine) for the database
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"options": "-csearch_path=public"})
    logger.info(f"Connection to the {DATABASE_HOST} for user {DATABASE_USER} created successfully.")
except Exception as ex:
    logger.error("Connection could not be made due to the following error:", ex)

def init_db():
    SQLModel.metadata.create_all(engine)

# Dependency to get the SQLModel session
def get_db():
    with Session(engine) as session:
        yield session

