from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# 인덱싱추천
#await collection.create_index("username", unique=True)
#await collection.create_index("email", unique=True)

class User(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    username: str
    email: EmailStr
    password_hash: str
    created_at: datetime
    is_active: bool = True
    roles: list[str] = Field(default_factory=lambda: ["user"])

class Portfolio(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: str  # MongoDB의 ObjectId를 str로 저장
    코드: str
    종목명: str | None = None
    purchase_date: datetime
    purchase_price: float
    quantity: int

    target_price: float | None = None
    stop_loss_price: float | None = None
    memo: str | None = None
    tags: list[str] | None = []
    is_favorite: bool = False
    last_updated: datetime | None = None

