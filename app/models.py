import datetime
from typing import Tuple

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index

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


class Sale(db.Model, ModelUtils):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)

    # Split `date` into 3 separate fields
    year = db.Column(db.String(4), nullable=False)
    month = db.Column(db.String(2), nullable=False)
    day = db.Column(db.String(2), nullable=False)

    # Indexed versions of `year` and `month` fields
    indexed_year = db.Column(db.String(4), nullable=False)
    indexed_month = db.Column(db.String(2), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    revenue = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)

    __table_args__ = (
        Index('idx_year_month', indexed_year, indexed_month),
    )

    @classmethod
    def new(cls, date: datetime.date, product: Product, revenue: float, region: Region) -> 'Sale':
        year, month, day = date.strftime('%Y-%m-%d').split('-')
        return super().new(
            date=date,
            year=year,
            month=month,
            day=day,
            indexed_year=year,
            indexed_month=month,
            product_id=product.id,
            revenue=revenue,
            region_id=region.id
        )
