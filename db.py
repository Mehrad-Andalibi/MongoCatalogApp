"""
db.py
MongoDB connection helper for the Web Catalog application.

This module ONLY handles:
- reading configuration from environment variables
- creating a MongoClient
- returning a handle to the database and products collection

Other business logic (CRUD, aggregation, etc.) should go in separate modules.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env if present
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "product_catalog")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "products")


_client: MongoClient | None = None


def get_client() -> MongoClient:
    """Return a singleton MongoClient instance."""
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client


def get_db():
    """Return the MongoDB database handle."""
    client = get_client()
    return client[DB_NAME]


def get_products_collection():
    """Return the products collection handle."""
    db = get_db()
    return db[COLLECTION_NAME]
