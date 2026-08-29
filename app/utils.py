from bson import ObjectId
from bson.errors import InvalidId


def to_object_id(id_str: str) -> ObjectId:
    """Converts a string id to a Mongo ObjectId, raising ValueError on bad format
    so callers can turn it into a clean 400/404 response instead of a 500."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise ValueError(f"'{id_str}' is not a valid id")


def serialize_restaurant(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "location": doc.get("location"),
        "rating": doc.get("rating", 0.0),
    }


def serialize_menu_item(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "restaurant_id": doc["restaurant_id"],
        "name": doc["name"],
        "price": doc["price"],
        "available": doc.get("available", True),
    }
