from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)

ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")

if not ASYNC_DATABASE_URL:
    raise RuntimeError("ASYNC_DATABASE_URL is not set.")

engine = create_async_engine(ASYNC_DATABASE_URL)