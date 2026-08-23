from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.session import Session
from app.schemas.session import SessionCreate
from app.services.conversation_service import ConversationService

router = APIRouter(tags=["sessions"])


@router.post("/sessions")
async def create_session(
    payload: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    session = Session(customer_id=payload.customer_id)

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "session_id": session.id,
        "customer_id": session.customer_id
    }


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: int,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve conversation history for a session.
    Used for context building (RAG / Chat).
    """

    messages = await ConversationService.get_messages_for_session(
        db=db,
        session_id=session_id,
        limit=limit,
    )

    if not messages:
        return {
            "session_id": session_id,
            "messages": [],
        }

    return {
        "session_id": session_id,
        "messages": messages,
    }
