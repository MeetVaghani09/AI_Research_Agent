from pydantic import BaseModel


class ResearchRequest(BaseModel):
    session_id: str
    question: str
