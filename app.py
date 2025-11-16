"""
app.py
FastAPI application entry point for the MongoCatalogApp.

Implements:
- Health check
- CRUD routes for products
- Review operations (push, positional update, arrayFilters update)
- Aggregation routes (average rating, review counts)
- Index creation route
- Uses inline Pydantic models for validation
"""

from fastapi import FastAPI
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, condecimal, conint
from services import products   # <-- all DB logic here


# ================================================================
# FastAPI Initialization
# ================================================================

app = FastAPI(
    title="MongoDB Web Catalog",
    description="Demo app for CST8276 - Advanced Database Topics",
    version="0.1.0",
)


# ================================================================
# Pydantic Models (Used for validation)
# ================================================================

class Review(BaseModel):
    """Represents a single review inside a product."""
    review_id: str
    user_id: str
    rating: conint(ge=1, le=5)
    comment: Optional[str] = None
    verified: bool


class ReviewUpdate(BaseModel):
    """Partial update for a review (PATCH)."""
    user_id: Optional[str] = None
    rating: Optional[conint(ge=1, le=5)] = None
    comment: Optional[str] = None
    verified: Optional[bool] = None


class ReviewArrayFilterUpdate(BaseModel):
    """
    Used for advanced arrayFilters updates.
    Example:
    {
      "filter_criteria": {"review_id": "r1001-1"},
      "new_data": {"rating": 5}
    }
    """
    filter_criteria: Dict[str, Any]
    new_data: Dict[str, Any]


class ProductCreate(BaseModel):
    """Model for creating a new product."""
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
    """Returned in GET operations."""
    sku: str
    name: str
    price: float
    category: Optional[str] = None
    reviews: List[Review] = []


# ================================================================
# Health Check
# ================================================================

@app.get("/health")
async def health_check():
    """Simple endpoint to make sure the API is running."""
    return {"status": "ok"}


# ================================================================
# Product CRUD Routes
# ================================================================

@app.get("/products", response_model=List[ProductOut])
async def list_products():
    """Return ALL products."""
    return products.get_all_products()


@app.get("/products/{sku}", response_model=ProductOut)
async def get_product(sku: str):
    """Return a single product by SKU."""
    return products.get_product(sku)


@app.post("/products", response_model=ProductOut, status_code=201)
async def create_product(body: ProductCreate):
    """Create a new product."""
    return products.create_product(body.model_dump())


@app.patch("/products/{sku}", response_model=ProductOut)
async def update_product(sku: str, body: ProductUpdate):
    """Update a product (partial update)."""
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    return products.update_product(sku, update_data)


@app.delete("/products/{sku}", status_code=204)
async def delete_product(sku: str):
    """Delete a product."""
    products.delete_product(sku)
    return


# ================================================================
# Review Routes
# ================================================================

@app.post("/products/{sku}/reviews", response_model=ProductOut, status_code=201)
async def add_review(sku: str, review: Review):
    """Add a review to a product."""
    return products.add_review(sku, review.model_dump())


@app.patch("/products/{sku}/reviews/{review_id}", response_model=ProductOut)
async def update_review_positional(sku: str, review_id: str, body: ReviewUpdate):
    """Update a single review using positional operator ($)."""
    return products.update_review_positional(sku, review_id, body.model_dump(exclude_none=True))


@app.patch("/products/{sku}/reviews/arrayfilters", response_model=ProductOut)
async def update_review_arrayfilters(sku: str, body: ReviewArrayFilterUpdate):
    """Update reviews using arrayFilters."""
    return products.update_review_array_filters(
        sku,
        body.filter_criteria,
        body.new_data
    )


# ================================================================
# Aggregation Routes
# ================================================================

@app.get("/products/ratings/summary")
async def ratings_summary():
    """
    Returns:
    - avg_rating per product
    - review_count per product

    Useful for reporting & dashboard stats.
    """
    return products.get_ratings_summary()


@app.get("/products/{sku}/rating")
async def rating_for_product(sku: str):
    """
    Returns:
    - average rating for ONE SKU

    Used when showing product details or analytics.
    """
    return products.get_rating_for_sku(sku)


# ================================================================
# Index Route
# ================================================================

@app.post("/products/indexes")
async def create_indexes():
    """
    Creates important indexes:
    - sku (unique)
    - reviews.review_id (for fast lookup)

    Returns list of indexes.
    """
    return products.ensure_indexes()
