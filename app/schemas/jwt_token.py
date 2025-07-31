from pydantic import BaseModel


class Token(BaseModel):
    sub: str
    role: str
    exp: int