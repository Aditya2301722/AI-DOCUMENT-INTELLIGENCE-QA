from pydantic import BaseModel


class SessionCreate(BaseModel):
    customer_id: int