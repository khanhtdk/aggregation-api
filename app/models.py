import datetime
from typing import Tuple

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index

from . import app
db = SQLAlchemy(app)


class ModelUtils:
    """Convenient utilities for CRUD operations."""

    @classmethod
    def new(cls, **kwargs) -> db.Model:
        """
        Newly creates a model object.

        :param kwargs:    Required fields for creating the object.
        """
        obj = cls(**kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj

    @classmethod
    def get_or_create(cls, defaults=None, **queries) -> Tuple[db.Model, bool]:
        """
        Looks up the object against the input queries, creates one if not existed,
        then returns the object.

        :param defaults:    A mapping of field-value pairs serves as supplement
                            info that is useful for creating the object.
        :param queries:     Keyword arguments (mandatory fields) required for
                            querying and creating the object.
        """
        obj = db.session.query(cls).filter_by(**queries).one_or_none()
        existed = obj is not None
        if not existed:
            defaults = defaults or {}
            obj = cls.new(**queries, **defaults)
        return obj, not existed


class Product(db.Model, ModelUtils):
    """Contains all available products."""

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)


class Region(db.Model, ModelUtils):
    """Contains all available regions."""

    __tablename__ = 'regions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)


class Sale(db.Model, ModelUtils):
    """
    This table contains all sales data ingested by the `ingest.py` script and is
    created for testing purpose only. Though it contains duplicated fields,
    those fields are intentionally added in order to support validating and
    experimenting the performance tests.
    """

    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    revenue = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)

    # Indexed version of `date` field
    indexed_date = db.Column(db.Date, nullable=False, index=True)

    # Split `date` into 3 separate fields
    year = db.Column(db.String(4), nullable=False)
    month = db.Column(db.String(2), nullable=False)
    day = db.Column(db.String(2), nullable=False)

    # Indexed versions of `year` and `month` fields
    indexed_year = db.Column(db.String(4), nullable=False)
    indexed_month = db.Column(db.String(2), nullable=False)

    # No indexed foreign keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)

    # Indexed foreign keys
    indexed_product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    indexed_region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False, index=True)

    __table_args__ = (
        # Composite index for `indexed_year` and `indexed_month`
        Index('idx_year_month', indexed_year, indexed_month),
    )

    @classmethod
    def new(cls, date: datetime.date, product: Product, revenue: float, region: Region) -> 'Sale':
        year, month, day = date.strftime('%Y-%m-%d').split('-')
        return super().new(
            date=date,
            indexed_date=date,
            year=year,
            month=month,
            day=day,
            indexed_year=year,
            indexed_month=month,
            product_id=product.id,
            region_id=region.id,
            indexed_product_id=product.id,
            indexed_region_id=region.id,
            revenue=revenue,
        )
