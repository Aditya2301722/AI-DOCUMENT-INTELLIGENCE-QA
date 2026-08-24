from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag import async_answer_query


router = APIRouter()


class ChatRequest(BaseModel):
    session_id: int = Field(
        ...,
        example=1,
        description="Application chat session ID",
    )

    message: str = Field(
        ...,
        example="How long can damaged products be returned?",
    )


class ChatResponse(BaseModel):
    answer: str
    sources: list = []


@router.post(
    "/query",
    response_model=ChatResponse,
    tags=["chat"],
)
async def query_chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Empty message",
        )

    try:
        response = await async_answer_query(
            session_id=req.session_id,
            message=req.message,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return response