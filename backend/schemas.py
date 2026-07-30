"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

# ─── Products ─────────────────────────────────────────────────────────────────

T = TypeVar("T")


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., max_length=1000)
    price: float = Field(..., ge=0)
    category: str = Field(..., min_length=1, max_length=100)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    photo_url: str
    created_at: str
    updated_at: str


class ProductListData(BaseModel):
    success: bool = True
    time: str = ""
    message: str = "Products fetched successfully"
    total_products: int = 0
    offset: int = 0
    limit: int = 10
    products: list[ProductResponse] = []


class ProductDetailData(BaseModel):
    success: bool = True
    time: str = ""
    message: str = ""
    product: Optional[ProductResponse] = None


class DeleteResponse(BaseModel):
    success: bool = True
    message: str = ""


# ─── Users ────────────────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=50)
    status: str = Field(default="Active", max_length=50)
    role: str = Field(..., max_length=100)


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=100)


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    status: str
    role: str
    created_at: str
    updated_at: str


class UserListData(BaseModel):
    success: bool = True
    time: str = ""
    message: str = "Users fetched successfully"
    total_users: int = 0
    offset: int = 0
    limit: int = 10
    users: list[UserResponse] = []


class UserDetailData(BaseModel):
    success: bool = True
    time: str = ""
    message: str = ""
    user: Optional[UserResponse] = None


def utcnow() -> str:
    return datetime.utcnow().isoformat()
