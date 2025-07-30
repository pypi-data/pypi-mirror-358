from typing import Optional

from pydantic import BaseModel


class PhoneNumber(BaseModel):
    country_code: int
    national_number: int
    extension: Optional[str] = None
    italian_leading_zero: Optional[bool] = None
    number_of_leading_zeros: Optional[int] = None
    preferred_domestic_carrier_code: Optional[int] = None
