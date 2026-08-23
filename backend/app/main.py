from fastapi import FastAPI
from sqlalchemy import text

# import the error-handling middleware
#from app.utils.errors import GlobalErrorMiddleware

# import chat router
from app.api.chat import router as chat_router

# import database engine
from app.db.database import engine

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.session import get_db
from app.api.customers import router as customer_router
from app.api.sessions import router as session_router
from app.api.messages import router as message_router






# create FastAPI application
app = FastAPI(
    title="Production-Grade RAG + CAG Chatbot",
    version="0.1.0",
    description="Backend API for a multilingual RAG + CAG chatbot"
)

# register global error-handling middleware
#app.add_middleware(GlobalErrorMiddleware)

# register chat routes
app.include_router(chat_router, prefix="/chat")

# register customer routes
app.include_router(customer_router)
# register session routes
app.include_router(session_router)
app.include_router(message_router)




# basic health check endpoint
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
# database health check endpoint
@app.get("/db/health", tags=["health"])
async def db_health(db: AsyncSession = Depends(get_db)):
    """
    Checks database connectivity.
    """
    result = await db.execute(text("SELECT 1"))
    return {"db": "connected", "result": result.scalar()}



# database connectivity check (TEMPORARY, for learning)
@app.get("/db-check", tags=["debug"])
async def db_check():
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        return {"db": "connected", "result": result.scalar()}
