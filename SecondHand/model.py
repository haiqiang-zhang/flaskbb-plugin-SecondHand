import datetime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey

Base = declarative_base()

class Items(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    items_name = Column(String)
    price = Column(Float)
    sellerID = Column(Integer)
    buyerID = Column(Integer)
    post_date = Column(DateTime)
    start_transaction_date = Column(DateTime)
    success_transaction_date = Column(DateTime)
    main_picture_url = Column(String)
    description = Column(String)
    buyer_phone = Column(String)
    buyer_email = Column(String)
    buyer_location = Column(String)
    buyer_comment = Column(String)
    orderStatusId = Column(Integer, ForeignKey('orderStatus.id'))

class Items_del(Base):
    __tablename__ = 'items_del'
    del_id = Column(Integer, primary_key=True)
    prev_id = Column(Integer)
    items_name = Column(String)
    price = Column(Float)
    sellerID = Column(Integer)
    buyerID = Column(Integer)
    post_date = Column(DateTime)
    start_transaction_date = Column(DateTime)
    success_transaction_date = Column(DateTime)
    main_picture_url = Column(String)
    description = Column(String)
    buyer_phone = Column(String)
    buyer_email = Column(String)
    buyer_location = Column(String)
    buyer_comment = Column(String)
    orderStatusId = Column(Integer, ForeignKey('orderStatus.id'))
    del_date = Column(DateTime)


class orderStatus(Base):
    __tablename__ = 'orderStatus'
    id = Column(Integer, primary_key=True)
    StatusName = Column(String)
    Items = relationship("Items", backref="orderStatus")
    Items_del = relationship("Items_del", backref="orderStatus")


