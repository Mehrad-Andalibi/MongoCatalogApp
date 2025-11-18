# services/products.py
#
# This file contains ALL MongoDB logic for the Web Catalog project.
#
# FastAPI routes call these functions --> these functions talk directly
# to MongoDB using PyMongo.
#
# CONTENTS:
#   CRUD operations for products
#   Add review
#   Update review (positional operator)
#   Update review (arrayFilters)
#   Aggregation pipelines (avg rating, review count)
#   Index creation
#

from fastapi import HTTPException, status
from db import get_products_collection
from pymongo.errors import PyMongoError
from pymongo import ASCENDING
import logging


# -------------------------------------------------------------
# Logging configuration
# -------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(name)s:%(message)s"
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------
# Helper: get collection
# -------------------------------------------------------------
def _coll():
    """Returns the MongoDB 'products' collection."""
    return get_products_collection()


# -------------------------------------------------------------
# Helper: throw 404
# -------------------------------------------------------------
def _not_found(sku: str):
    """Raises a 404 HTTP error if product is missing."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product with SKU '{sku}' not found"
    )


# -------------------------------------------------------------
# ---------------------- CRUD OPERATIONS -----------------------
# -------------------------------------------------------------

def create_product(product_data: dict):
    """
    Create a new product in MongoDB.

    Steps:
      1. Check for duplicate SKU
      2. Insert product
      3. Return created product without _id
    """
    coll = _coll()

    # Prevent duplicate SKU
    if coll.find_one({"sku": product_data["sku"]}):
        raise HTTPException(status_code=409, detail="SKU already exists")

    # Insert
    result = coll.insert_one(product_data)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to insert product")

    # Return clean result
    return coll.find_one({"sku": product_data["sku"]}, {"_id": 0})


def get_product(sku: str):
    """Return a single product by SKU."""
    coll = _coll()
    doc = coll.find_one({"sku": sku}, {"_id": 0})

    if not doc:
        _not_found(sku)

    return doc


def get_all_products():
    """
    Return all products.
    Removes _id to keep JSON clean.
    """
    coll = _coll()
    return list(coll.find({}, {"_id": 0}))


def update_product(sku: str, update_data: dict):
    """
    Update a product using $set.

    Example:
      update_product("SKU1001", {"price": 149.99})
    """
    coll = _coll()
    res = coll.update_one({"sku": sku}, {"$set": update_data})

    if res.matched_count == 0:
        _not_found(sku)

    return coll.find_one({"sku": sku}, {"_id": 0})


def delete_product(sku: str):
    """Delete a product by SKU."""
    coll = _coll()
    res = coll.delete_one({"sku": sku})

    if res.deleted_count == 0:
        _not_found(sku)

    return {"message": f"Product '{sku}' deleted successfully"}


# -------------------------------------------------------------
# ---------------------- REVIEW OPERATIONS ---------------------
# -------------------------------------------------------------

def add_review(sku: str, review_data: dict):
    """
    Add a review to a product.
    Uses $push to append to 'reviews' array.
    """
    coll = _coll()

    res = coll.update_one(
        {"sku": sku},
        {"$push": {"reviews": review_data}}
    )

    if res.matched_count == 0:
        _not_found(sku)

    return coll.find_one({"sku": sku}, {"_id": 0})


def update_review_positional(sku: str, review_id: str, update_data: dict):
    """
    Update ONE review using MongoDB positional operator ($).

    Example:
        update_data = { "rating": 4 }
        becomes:
            { "$set": { "reviews.$.rating": 4 } }
    """
    coll = _coll()

    # Convert update_data to paths like reviews.$.rating
    update_fields = {f"reviews.$.{k}": v for k, v in update_data.items()}

    res = coll.update_one(
        {"sku": sku, "reviews.review_id": review_id},
        {"$set": update_fields}
    )

    if res.matched_count == 0:
        _not_found(sku)

    return coll.find_one({"sku": sku}, {"_id": 0})


def update_review_array_filters(sku: str, filter_criteria: dict, new_data: dict):
    """
    Advanced review update using arrayFilters.

    Example:
        filter_criteria = { "review_id": "r1001-2" }
        new_data        = { "rating": 3 }

    Produces:
        $set: { "reviews.$[rev].rating": 3 }
        arrayFilters: [ { "rev.review_id": "r1001-2" } ]
    """
    coll = _coll()

    # Build update paths
    update_fields = {f"reviews.$[rev].{k}": v for k, v in new_data.items()}

    # Build arrayFilters object
    array_filters = [
        {f"rev.{k}": v for k, v in filter_criteria.items()}
    ]

    res = coll.update_one(
        {"sku": sku},
        {"$set": update_fields},
        array_filters=array_filters
    )

    if res.matched_count == 0:
        _not_found(sku)

    return coll.find_one({"sku": sku}, {"_id": 0})


# -------------------------------------------------------------
# ------------------ AGGREGATION OPERATIONS -------------------
# -------------------------------------------------------------

def get_ratings_summary():
    """
    Get rating summary for ALL products:
      - review_count
      - avg_rating (null if none)

    Uses:
      $project, $size, $avg, $ifNull, $cond
    """
    coll = _coll()

    pipeline = [
        {
            "$project": {
                "_id": 0,
                "sku": 1,
                "name": 1,
                "price": 1,

                # Count reviews safely
                "review_count": {
                    "$size": {"$ifNull": ["$reviews", []]}
                },

                # Compute avg if there are reviews
                "avg_rating": {
                    "$cond": [
                        { "$gt": [ { "$size": {"$ifNull": ["$reviews", []]} }, 0 ] },
                        { "$avg": "$reviews.rating" },
                        None
                    ]
                }
            }
        }
    ]

    return list(coll.aggregate(pipeline))


def get_rating_for_sku(sku: str):
    """
    Aggregation for ONE product using:
      $match --> pick product
      $unwind --> flatten reviews
      $group --> compute avg + count 
    """
    coll = _coll()

    pipeline = [
        {"$match": {"sku": sku}},
        {"$unwind": "$reviews"},
        {
            "$group": {
                "_id": "$sku",
                "name": { "$first": "$name" },
                "avg_rating": { "$avg": "$reviews.rating" },
                "review_count": { "$sum": 1 }
            }
        },
        {
            "$project": {
                "_id": 0,
                "sku": "$_id",
                "name": 1,
                "avg_rating": 1,
                "review_count": 1
            }
        }
    ]

    result = list(coll.aggregate(pipeline))

    if not result:
        _not_found(sku)

    return result[0]


# -------------------------------------------------------------
# --------------------- INDEXING OPERATIONS -------------------
# -------------------------------------------------------------

def ensure_indexes():
    """
    Create recommended indexes:
      1. sku (unique)
      2. reviews.review_id
      3. price

    Returns:
      index_information() for screenshots/report.
    """
    coll = _coll()

    coll.create_index("sku", unique=True, name="idx_sku_unique")
    coll.create_index("reviews.review_id", name="idx_reviews_review_id")
    coll.create_index([("price", ASCENDING)], name="idx_price")

    return coll.index_information()
