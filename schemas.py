"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Arabic-fashion focused schemas

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema for Arabic dress storefront
    Collection name: "product"
    """
    title_ar: str = Field(..., description="Arabic product title")
    description_ar: Optional[str] = Field(None, description="Arabic description")
    price: float = Field(..., ge=0, description="Current price (SAR)")
    original_price: Optional[float] = Field(None, ge=0, description="Original price before discount (SAR)")
    discount_percent: Optional[int] = Field(None, ge=0, le=100, description="Discount in percent e.g. 30")
    category: Optional[str] = Field("فساتين", description="Category name in Arabic")
    in_stock: bool = Field(True, description="Whether product is in stock")
    sizes: List[str] = Field(default_factory=lambda: ["S", "M", "L", "XL"], description="Available sizes")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    sku: Optional[str] = Field(None, description="Model number / SKU")

# Add other collections later as needed (wishlist, orders, etc.)
