import datetime
from typing import Tuple

from flask_sqlalchemy import SQLAlchemy
from . import app

db = SQLAlchemy(app)


class ModelUtils:
    @classmethod
    def new(cls, **kwargs) -> db.Model:
        obj = cls(**kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj

    @classmethod
    def get_or_create(cls, defaults=None, **queries) -> Tuple[db.Model, bool]:
        obj = db.session.query(cls).filter_by(**queries).one_or_none()
        existed = obj is not None
        if not existed:
            defaults = defaults or {}
            obj = cls.new(**queries, **defaults)
        return obj, not existed


class Product(db.Model, ModelUtils):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)


class Region(db.Model, ModelUtils):
    __tablename__ = 'regions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)


class Order(db.Model, ModelUtils):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    date_purchased = db.Column(db.Date, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    revenue = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)

    @classmethod
    def new(cls, date_purchased: datetime.date, product: Product, revenue: float, region: Region) -> 'Order':
        return super().new(
            date_purchased=date_purchased,
            product_id=product.id,
            revenue=revenue,
            region_id=region.id
        )


class SplitDateOrder(db.Model, ModelUtils):
    __tablename__ = 'split_date_orders'

    id = db.Column(db.Integer, primary_key=True)

    # Split `date_purchased` into 3 separate fields
    year = db.Column(db.String(4), nullable=False)
    month = db.Column(db.String(2), nullable=False)
    day = db.Column(db.String(2), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    revenue = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)

    @classmethod
    def new(cls, date_purchased: datetime.date, product: Product, revenue: float, region: Region) -> 'Order':
        year, month, day = date_purchased.strftime('%Y-%m-%d').split('-')
        return super().new(
            date_purchased=date_purchased,
            year=year,
            month=month,
            day=day,
            product_id=product.id,
            revenue=revenue,
            region_id=region.id
        )
