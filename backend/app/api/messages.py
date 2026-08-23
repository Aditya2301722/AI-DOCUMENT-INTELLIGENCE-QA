from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.message import MessageCreate
from app.services.conversation_service import ConversationService

router = APIRouter(tags=["messages"])


@router.post("/messages")
async def create_message(
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a message via ConversationService.
    All validation and persistence logic lives in the service layer.
    """
    try:
        message = await ConversationService.add_message(
            db=db,
            session_id=payload.session_id,
            role=payload.role,
            content=payload.content,
        )
        return message

    except ValueError as e:
        # Service-layer validation errors
        raise HTTPException(status_code=400, detail=str(e))
