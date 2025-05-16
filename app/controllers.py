from sqlalchemy import text
from .models import db


def query_monthly_sales():
    query = '''
        SELECT
            STRFTIME('%Y', date_purchased) AS year,
            STRFTIME('%m', date_purchased) AS month,
            SUM(revenue) AS total_revenue
        FROM orders
        GROUP BY year, month
        ORDER BY year, month
    '''
    cursor = db.session.execute(text(query))
    columns = list(cursor.keys())
    return list(map(lambda i: dict(zip(columns, i)), cursor.all()))


