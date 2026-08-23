import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not set.")


with psycopg.connect(database_url) as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT extname, extversion
            FROM pg_extension
            WHERE extname = 'vector';
            """
        )

        result = cursor.fetchone()

        if result:
            print("PGVECTOR: ENABLED")
            print("EXTENSION:", result[0])
            print("VERSION:", result[1])
        else:
            print("PGVECTOR: NOT FOUND")