from pydantic import BaseModel


class TestSet(BaseModel):
    id: str
    type: str
    governmentId: str
    idCompany: str
