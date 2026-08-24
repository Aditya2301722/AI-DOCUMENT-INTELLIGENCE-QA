from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ============================================================
# Routers
# ============================================================

from app.api.chat import router as chat_router
from app.api.customers import router as customer_router
from app.api.documents import router as document_router
from app.api.messages import router as message_router
from app.api.sessions import router as session_router

# ============================================================
# Database
# ============================================================

from app.db.database import engine
from app.db.session import get_db


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Production-Grade RAG + CAG Chatbot",
    version="0.1.0",
    description="Backend API for a multilingual RAG + CAG chatbot",
)


# ============================================================
# CORS
# ============================================================
#
# React frontend:
#   http://localhost:5173
#
# FastAPI backend:
#   http://127.0.0.1:8000
#
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Routes
# ============================================================

# Chat
app.include_router(
    chat_router,
    prefix="/chat",
)

# Customers
app.include_router(
    customer_router,
)

# Sessions
app.include_router(
    session_router,
)

# Messages
app.include_router(
    message_router,
)

# Documents
app.include_router(
    document_router,
)


# ============================================================
# Health Check
# ============================================================

@app.get(
    "/health",
    tags=["health"],
)
def health():
    return {
        "status": "ok",
    }


# ============================================================
# Database Health Check
# ============================================================

@app.get(
    "/db/health",
    tags=["health"],
)
async def db_health(
    db: AsyncSession = Depends(get_db),
):
    """
    Checks database connectivity.
    """

    result = await db.execute(
        text("SELECT 1")
    )

    return {
        "db": "connected",
        "result": result.scalar(),
    }


# ============================================================
# Database Debug Check
# ============================================================

@app.get(
    "/db-check",
    tags=["debug"],
)
async def db_check():
    """
    Temporary database connectivity check.
    """

    async with engine.connect() as connection:

        result = await connection.execute(
            text("SELECT 1")
        )

        return {
            "db": "connected",
            "result": result.scalar(),
        }