import datetime

from flask_sqlalchemy import SQLAlchemy

from . import app

db = SQLAlchemy(app)


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)


class Region(db.Model):
    __tablename__ = 'regions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    date_purchased = db.Column(db.Date, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    revenue = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)


class SplitDateOrder(db.Model):
    __tablename__ = 'split_date_orders'

    id = db.Column(db.Integer, primary_key=True)

    # Split `date_purchased` into 3 separate fields
    year = db.Column(db.String(4), nullable=False)
    month = db.Column(db.String(2), nullable=False)
    day = db.Column(db.String(2), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    revenue = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)

    @property
    def date_purchased(self):
        return datetime.date(int(self.year), int(self.month), int(self.day))
