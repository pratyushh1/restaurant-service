from pydantic import BaseModel


class RestaurantCreate(BaseModel):
    name: str
    location: str | None = None
    rating: float = 0.0


class RestaurantOut(RestaurantCreate):
    id: str


class MenuItemCreate(BaseModel):
    name: str
    price: float
    available: bool = True


class MenuItemOut(MenuItemCreate):
    id: str
    restaurant_id: str
