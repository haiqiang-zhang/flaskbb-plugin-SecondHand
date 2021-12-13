from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime, Float, ForeignKey
)
from sqlalchemy.orm import mapper
from .model import Items

metadata = MetaData()

items_table = Table(
    'items', metadata,
    Column('items_id', Integer, primary_key=True, autoincrement=True),
    Column('items_name', String, nullable=False),
    Column('price', Float, nullable=False),
    Column('sellerID', Integer, nullable=False),
    Column('buyerID', Integer),
    Column('post_date', DateTime),
    Column('transaction_date', DateTime),
    Column('main_picture_url', String),
    Column('description', String)
)


def map_model_to_tables():
    mapper(Items, items_table, properties={
        '_Items__items_name': items_table.c.items_name,
        '_Items__price': items_table.c.price,
        '_Items__sellerID': items_table.c.sellerID,
        '_Items__buyerID': items_table.c.buyerID,
        '_Items__post_date': items_table.c.post_date,
        '_Items__transaction_date': items_table.c.transaction_date,
        '_Items__main_picture_url': items_table.c.main_picture_url,
        '_Items__description': items_table.c.description,
    })
