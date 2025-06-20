from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Enum, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.baselayer.basemodel import BaseModel
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from config.database import Base
import enum


class Category(BaseModel):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    is_active = Column(Boolean, default=True)

    parent = relationship("Category", remote_side=[id])
    children = relationship("Category", backref="parent_category", remote_side=[parent_id])
    books = relationship("Book", back_populates="category")


class BookFormat(str, enum.Enum):
    hardcover = 'hardcover'
    paperback = 'paperback'
    ebook = 'ebook'
    audiobook = 'audiobook'


class BookStatus(str, enum.Enum):
    active = 'active'
    inactive = 'inactive'
    out_of_stock = 'out_of_stock'


class Book(BaseModel):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(13), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255))
    author = Column(String(255), nullable=False)
    co_authors = Column(Text)
    publisher = Column(String(255))
    publication_date = Column(Date)
    pages = Column(Integer)
    language = Column(String(50))
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    discount_price = Column(Numeric(10, 2))
    stock_quantity = Column(Integer, default=0)
    cover_image_url = Column(String(500))
    format = Column(Enum(BookFormat), nullable=False)
    status = Column(Enum(BookStatus), default=BookStatus.active)
    category_id = Column(Integer, ForeignKey("categories.id"))

    category = relationship("Category", back_populates="books")
    reviews = relationship("Review", back_populates="book")


class Review(BaseModel):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    user_id = Column(Integer, ForeignKey("users.id"))  # Assuming user table exists
    rating = Column(Integer)  # 1 to 5, validate in Pydantic
    review_text = Column(Text)
    is_verified_purchase = Column(Boolean, default=False)

    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")  # Define this in user model
