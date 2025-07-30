from typing import Optional

from pydantic import BaseModel, EmailStr

from alegra.models.address import Address
from alegra.models.phone_number import PhoneNumber


class Customer(BaseModel):
    name: str
    organizationType: int
    identificationType: str
    identificationNumber: Optional[str]
    dv: Optional[str]
    email: Optional[EmailStr] = ""
    address: Optional[Address] = None
    phone: str = ""
