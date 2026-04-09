from pydantic import BaseModel


class LookupResponse(BaseModel):
    is_health: bool
    name: str | None = None
    type: str | None = None
    address: str | None = None
    whatsapp: str | None = None
    city: str | None = None
    notes: str | None = None
    matched_phone: str | None = None