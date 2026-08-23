import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

# load values from .env file
load_dotenv()

# read database address
DATABASE_URL = os.getenv("DATABASE_URL")

# create a connection manager (engine)
engine = create_async_engine(DATABASE_URL)

