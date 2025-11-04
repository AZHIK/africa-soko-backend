from sqlmodel import SQLModel


from app.models.product import Product, Category, Review  # noqa: F401
from app.models.order import Order, OrderItem  # noqa: F401
from app.models.vendor import Vendor  # noqa: F401
from app.models.wishlist_and_cart import WishlistItem, CartItem  # noqa: F401

# Alembic MetaData object for autogenerate
Base = SQLModel
