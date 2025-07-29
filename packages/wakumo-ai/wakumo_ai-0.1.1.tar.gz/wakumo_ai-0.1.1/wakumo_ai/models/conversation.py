from pydantic import BaseModel
from typing import Optional

class ConversationCreateResponse(BaseModel):
    status: str
    conversation_id: str

class ConversationInfo(BaseModel):
    conversation_id: str
    title: str
    selected_repository: Optional[str]
    last_updated_at: Optional[str]
    created_at: Optional[str]
    status: Optional[str]