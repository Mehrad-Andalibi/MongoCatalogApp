"""
seed.py
Insert initial sample data into the products collection.

Run:
    python seed.py
"""

from db import get_products_collection


def get_sample_products() -> list[dict]:
    """Return a list of sample product documents."""

    return [
        {
            "sku": "SKU1001",
            "name": "Wireless Headphones",
            "price": 129.99,
            "tags": ["audio", "bluetooth"],
            "reviews": [
                {
                    "review_id": "r1001-1",
                    "user_id": "u100",
                    "rating": 5,
                    "comment": "Excellent sound and battery life!",
                    "verified": True,
                },
                {
                    "review_id": "r1001-2",
                    "user_id": "u101",
                    "rating": 4,
                    "comment": "Great overall, a bit tight on the ears.",
                    "verified": True,
                },
            ],
        },
        {
            "sku": "SKU1002",
            "name": "Mechanical Keyboard",
            "price": 89.99,
            "tags": ["peripherals", "keyboard"],
            "reviews": [
                {
                    "review_id": "r1002-1",
                    "user_id": "u102",
                    "rating": 5,
                    "comment": "Amazing typing feel.",
                    "verified": False,
                }
            ],
        },
        {
            "sku": "SKU1003",
            "name": "4K Monitor",
            "price": 329.99,
            "tags": ["display", "monitor"],
            "reviews": [
                {
                    "review_id": "r1003-1",
                    "user_id": "u103",
                    "rating": 3,
                    "comment": "Good picture, but the stand is wobbly.",
                    "verified": True,
                }
            ],
        },
        {
            "sku": "SKU1004",
            "name": "USB-C Docking Station",
            "price": 74.99,
            "tags": ["peripherals", "dock"],
            "reviews": [],
        },
    ]


def main():
    collection = get_products_collection()

    # Clear existing data (for repeatable seeding in dev)
    collection.delete_many({})

    docs = get_sample_products()
    result = collection.insert_many(docs)
    print(f"Inserted {len(result.inserted_ids)} products.")

    # Show what we inserted
    for doc in collection.find():
        print(doc)


if __name__ == "__main__":
    main()
