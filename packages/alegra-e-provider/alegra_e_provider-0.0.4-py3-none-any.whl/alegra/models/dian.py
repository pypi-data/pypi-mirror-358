from pydantic import BaseModel


class DianResource(BaseModel):
    id: str
    name: str
