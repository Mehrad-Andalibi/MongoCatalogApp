"""
app.py
FastAPI application entry point for the MongoCatalogApp.

Implements:
- /health endpoint
- Full CRUD routes for the products collection
- Inline Pydantic models for validation (no external models.py required)
- Integration with MongoDB via db.py and services/products.py
"""

from fastapi import FastAPI
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, condecimal, conint
from datetime import datetime
from services import products  # CRUD logic lives in services/products.py


# ================================================================
# FastAPI Application Initialization
# ================================================================

app = FastAPI(
    title="MongoDB Web Catalog",
    description="Demo app for CST8276 - Advanced Database Topics",
    version="0.1.0",
)

# ================================================================
# Inline Pydantic Models (validation for requests/responses)
# ================================================================

class Review(BaseModel):
    """
    Represents a single review inside a product.
    Required:
    - review_id: unique id per review
    - user_id: who wrote the review
    - rating: 1–5 (validated)
    - verified: whether it's a verified purchase
    """
    review_id: str
    user_id: str
    rating: conint(ge=1, le=5)
    comment: Optional[str] = None
    verified: bool

class ReviewUpdate(BaseModel):
    """
    Partial update for a single review.
    All fields are optional so PATCH can send only what changes.
    """
    user_id: Optional[str] = None
    rating: Optional[conint(ge=1, le=5)] = None
    comment: Optional[str] = None
    verified: Optional[bool] = None

class ReviewArrayFilterUpdate(BaseModel):
    """
    Request body for arrayFilters-based updates.

    Example:
    {
      "filter_criteria": {"user_id": "u100"},
      "new_data": {"comment": "Edited by moderator"}
    }
    """
    filter_criteria: Dict[str, Any] = Field(
        ...,
        description="Criteria to match the review to update",
        example={"review_id": "r1001-1"}
    )
    new_data: Dict[str, Any] = Field(
        ...,
        description="New data to set on the matched review",
        example={"rating": 5, "comment": "Updated review text"}
    )

class ProductCreate(BaseModel):
    """
    Model for creating a new product.
    Used as request body for POST /products.
    """
    sku: str
    name: str
    price: condecimal(ge=0, max_digits=10, decimal_places=2)
    category: Optional[str] = None
    reviews: List[Review] = []


class ProductUpdate(BaseModel):
    """Model for updating an existing product."""
    name: Optional[str] = None
    price: Optional[condecimal(ge=0, max_digits=10, decimal_places=2)] = None
    category: Optional[str] = None


class ProductOut(BaseModel):
    """Model returned in API responses."""
    sku: str
    name: str
    price: float
    category: Optional[str] = None
    reviews: List[Review] = []


# ================================================================
# Health Check Endpoint
# ================================================================

@app.get("/health")
async def health_check():
    """
    Basic health check endpoint to verify the API is running.
    Returns {"status": "ok"} when operational.
    """
    return {"status": "ok"}


# ================================================================
# Product CRUD Endpoints
# ================================================================

@app.get("/products", response_model=List[ProductOut])
async def list_products():
    """
    Retrieve all products from the MongoDB collection.
    Returns a list of ProductOut models.
    """
    return products.get_all_products()


@app.get("/products/{sku}", response_model=ProductOut)
async def get_product(sku: str):
    """
    Retrieve a single product document by its SKU.
    Raises 404 if the product does not exist.
    """
    return products.get_product(sku)


@app.post("/products", response_model=ProductOut, status_code=201)
async def create_product(body: ProductCreate):
    """
    Create a new product document in MongoDB.
    - Validates request body using ProductCreate model.
    - Returns the newly inserted product.
    - Raises 409 if SKU already exists.
    """
    return products.create_product(body.model_dump())


@app.patch("/products/{sku}", response_model=ProductOut)
async def update_product(sku: str, body: ProductUpdate):
    """
    Update an existing product document by SKU.
    - Accepts partial updates.
    - Raises 404 if the product does not exist.
    """
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    return products.update_product(sku, update_data)


@app.delete("/products/{sku}", status_code=204)
async def delete_product(sku: str):
    """
    Delete a product document by SKU.
    - Raises 404 if SKU not found.
    - Returns 204 No Content on success.
    """
    products.delete_product(sku)
    return

@app.post("/products/{sku}/reviews", response_model=ProductOut, status_code=201)
async def add_review(sku: str, review: Review):
    """
    Add a review to a product.
    """
    return products.add_review(sku, review.model_dump())

@app.patch("/products/{sku}/reviews/{review_id}", response_model=ProductOut)
async def update_review_positional(sku: str, review_id: str, body: ReviewUpdate):
    """
    Update a single review in a product using the positional operator ($)."""
    return products.update_review_positional(sku, review_id, body.model_dump(exclude_none=True))

@app.patch("/products/{sku}/reviews/arrayfilters", response_model=ProductOut)
async def patch_review_with_arrayfilter(sku: str, body: ReviewArrayFilterUpdate):
    """
    Update reviews in a product using MongoDB arrayFilters.
    """
    return products.update_review_array_filters(
        sku,
        body.filter_criteria,
        body.new_data
    )
