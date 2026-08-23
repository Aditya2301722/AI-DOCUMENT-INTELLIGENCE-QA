from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.rag import async_answer_query

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str | None = Field(None, example="session-001")
    message: str = Field(..., example="Where is my order?")

class ChatResponse(BaseModel):
    answer: str
    sources: list = []

@router.post("/query", response_model=ChatResponse, tags=["chat"])
async def query_chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    response = await async_answer_query(
        session_id=req.session_id,
        message=req.message
    )
    return response
