import os
import csv
import sys
from argparse import ArgumentParser, Namespace
from datetime import datetime
from dataclasses import dataclass, field, InitVar
from typing import List

from app import app
from app.models import db, Sale, Product, Region


class CsvData:
    """Parsed rows of CSV file content."""

    @dataclass
    class RowData:
        """Data struct that parses a single row of CSV file."""

        # Mandatory fields
        sale_date: datetime.date = field(init=False)
        product_name: str = field(init=False)
        revenue: float = field(init=False)
        sale_region: str = field(init=False)

        # Accepts raw data of the CSV row as input
        csv_row: InitVar[List[str]]

        def __post_init__(self, csv_row: List[str]):
            # Parse fields from row data
            try:
                date, prod, revenue, region = csv_row
                assert date and prod and revenue and region, 'fields must be all set'
                assert isinstance(prod, str), 'product_name must be string'
                assert isinstance(region, str), 'sale_region must be string'
                date = datetime.strptime(date, '%Y-%m-%d').date()
                revenue = float(revenue)
            except (ValueError, TypeError, AssertionError) as e:
                raise ValueError(e)

            # Update mandatory fields
            self.sale_date = date
            self.product_name = prod
            self.revenue = revenue
            self.sale_region = region

    @classmethod
    def from_file(cls, csv_file: str, has_header: bool) -> 'CsvData':
        """
        Construct object by reading from a CSV file.

        :param csv_file:        Path to CSV file
        :param has_header:      Whether the CSV file has a header row
        """

        if not os.path.isfile(csv_file):
            raise FileNotFoundError(f'File {csv_file!r} not found')

        rows = []
        with open(csv_file, newline='') as fp:
            for idx, row in enumerate(csv.reader(fp)):
                if has_header and idx == 0:
                    continue  # skip header
                try:
                    rows.append(cls.RowData(csv_row=row))
                except ValueError as e:
                    raise ValueError(f'File {csv_file!r} has invalid row data at line {idx+1}: {e}')

        return cls(rows)

    def __init__(self, rows: List[RowData]):
        self.rows = rows

    def __iter__(self):
        return iter(self.rows)

    def __bool__(self):
        return bool(self.rows)


def ingest(data: CsvData):
    """Method for ingesting CsvData into database."""
    # Exit if data is empty
    assert data, 'No data to ingest'

    # Start ingesting data
    for row in data:
        # Get or create region if not existed
        region, created = Region.get_or_create(name=row.sale_region)
        if created:
            print(f'Created {region!r}')

        # Get or create product if not existed
        product, created = Product.get_or_create(name=row.product_name)
        if created:
            print(f'Created {product!r}')

        # Created sale
        sale = Sale.new(row.sale_date, product, row.revenue, region)
        print(f'Created {sale!r}')


def get_args() -> Namespace:
    """Read arguments from command line."""

    parser = ArgumentParser(
        description='Ingest database from CSV file'
    )
    parser.add_argument(
        '--csv-file',
        metavar='FILE',
        default='sales-data.csv',
        help='CSV file to ingest (default: %(default)s)'
    )
    parser.add_argument(
        '--no-header',
        action='store_true',
        help='Whether CSV file has no header'
    )
    return parser.parse_args()


def main():
    args = get_args()
    data = CsvData.from_file(csv_file=args.csv_file, has_header=not args.no_header)
    with app.app_context():
        db.create_all()
        ingest(data)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, FileNotFoundError, AssertionError) as e:
        print(e, file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        pass
