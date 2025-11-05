// validators.js
// Run this in mongosh against the correct database, e.g.:
//
//   use product_catalog
//   load("validators.js")
//
// It will create the "products" collection with a JSON schema validator
// that enforces rating between 1 and 5 and some required fields.

db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["sku", "name", "reviews"],
      properties: {
        sku: {
          bsonType: "string",
          description: "Unique product SKU (string) is required"
        },
        name: {
          bsonType: "string",
          description: "Product name is required"
        },
        tags: {
          bsonType: ["array"],
          items: {
            bsonType: "string"
          },
          description: "Optional array of tags"
        },
        reviews: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["review_id", "user_id", "rating"],
            properties: {
              review_id: {
                bsonType: "string",
                description: "Unique review id (within product)"
              },
              user_id: {
                bsonType: "string",
                description: "Id of user who wrote the review"
              },
              rating: {
                bsonType: "int",
                minimum: 1,
                maximum: 5,
                description: "Rating must be between 1 and 5"
              },
              comment: {
                bsonType: "string",
                description: "Optional comment text"
              },
              verified: {
                bsonType: "bool",
                description: "Optional flag indicating verified purchase"
              }
            }
          },
          description: "Array of embedded review documents"
        }
      }
    }
  }
});
