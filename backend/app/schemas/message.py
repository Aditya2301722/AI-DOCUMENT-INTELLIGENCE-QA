from pydantic import BaseModel


class MessageCreate(BaseModel):
    session_id: int
    role: str
    content: str