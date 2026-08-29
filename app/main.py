from fastapi import FastAPI, HTTPException
from pymongo.errors import PyMongoError
import time

from app.database import restaurants_collection, menu_items_collection, client as mongo_client
from app import schemas
from app.utils import to_object_id, serialize_restaurant, serialize_menu_item

app = FastAPI(title="restaurant-service")


@app.on_event("startup")
def on_startup():
    # Retry a few times in case the MongoDB container is still starting up
    # (docker-compose "depends_on" does not wait for Mongo to be ready).
    last_error = None
    for attempt in range(10):
        try:
            mongo_client.admin.command("ping")
            return
        except PyMongoError as e:
            last_error = e
            time.sleep(3)
    raise RuntimeError(f"Could not connect to MongoDB after retries: {last_error}")


@app.get("/health")
def health():
    return {"status": "restaurant-service is up"}


# ---- Restaurants ----

@app.post("/restaurants", response_model=schemas.RestaurantOut)
def create_restaurant(restaurant: schemas.RestaurantCreate):
    result = restaurants_collection.insert_one(restaurant.model_dump())
    doc = restaurants_collection.find_one({"_id": result.inserted_id})
    return serialize_restaurant(doc)


@app.get("/restaurants", response_model=list[schemas.RestaurantOut])
def list_restaurants():
    return [serialize_restaurant(doc) for doc in restaurants_collection.find()]


@app.get("/restaurants/{restaurant_id}", response_model=schemas.RestaurantOut)
def get_restaurant(restaurant_id: str):
    try:
        oid = to_object_id(restaurant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    doc = restaurants_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return serialize_restaurant(doc)


# ---- Menu items ----

@app.post("/restaurants/{restaurant_id}/menu", response_model=schemas.MenuItemOut)
def add_menu_item(restaurant_id: str, item: schemas.MenuItemCreate):
    try:
        oid = to_object_id(restaurant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not restaurants_collection.find_one({"_id": oid}):
        raise HTTPException(status_code=404, detail="Restaurant not found")

    item_doc = item.model_dump()
    item_doc["restaurant_id"] = restaurant_id
    result = menu_items_collection.insert_one(item_doc)
    doc = menu_items_collection.find_one({"_id": result.inserted_id})
    return serialize_menu_item(doc)


@app.get("/restaurants/{restaurant_id}/menu", response_model=list[schemas.MenuItemOut])
def get_menu_for_restaurant(restaurant_id: str):
    docs = menu_items_collection.find({"restaurant_id": restaurant_id})
    return [serialize_menu_item(doc) for doc in docs]


# THIS IS THE ENDPOINT order-service calls to validate an item and get its price.
@app.get("/menu/{item_id}", response_model=schemas.MenuItemOut)
def get_menu_item(item_id: str):
    try:
        oid = to_object_id(item_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    doc = menu_items_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return serialize_menu_item(doc)
