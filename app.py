"""
app.py
FastAPI application entry point.

Currently provides:
- /health endpoint
- Skeleton routes for future implementation

Teammates will implement actual CRUD and nested-array logic
using functions from db.py (and other service modules).
"""

from fastapi import FastAPI
from db import get_products_collection

app = FastAPI(
    title="MongoDB Web Catalog",
    description="Demo app for CST8276 - Advanced Database Topics",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}


# ===== Skeleton endpoints for teammates to implement =====

@app.get("/products")
async def list_products():
    """
    TODO (Teammate):
    - Fetch products from MongoDB (maybe with paging later)
    - Return as JSON
    """
    # Example placeholder so the route works:
    coll = get_products_collection()
    sample_count = coll.count_documents({})
    return {"message": "Not implemented yet", "sample_product_count": sample_count}


@app.post("/products")
async def create_product():
    """
    TODO (Teammate):
    - Validate request body
    - Insert new product document
    - Handle validation errors from MongoDB
    """
    return {"message": "create_product not implemented yet"}


@app.post("/products/{sku}/reviews")
async def add_review(sku: str):
    """
    TODO (Teammate):
    - Read review data from request body
    - Use $push to append review to the product's reviews[]
    """
    return {"message": f"add_review for {sku} not implemented yet"}


@app.patch("/products/{sku}/reviews/{review_id}")
async def update_review(sku: str, review_id: str):
    """
    TODO (Teammate):
    - Use positional $ operator or arrayFilters to update a specific review
    """
    return {
        "message": f"update_review for sku={sku}, review_id={review_id} not implemented yet"
    }


@app.get("/products/{sku}/rating")
async def get_product_rating(sku: str):
    """
    TODO (Teammate):
    - Use aggregation pipeline to compute average rating for one product
    - Optionally reuse Mehrad's aggregation helper function if provided
    """
    return {"message": f"get_product_rating for {sku} not implemented yet"}
