import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime

Base = declarative_base()

class Items(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    items_name = Column(String)
    price = Column(Float)
    sellerID = Column(Integer)
    buyerID = Column(Integer)
    post_date = Column(DateTime)
    transaction_date = Column(DateTime)
    main_picture_url = Column(String)
    description = Column(String)

    # def __init__(self, items_name: str, price: float, sellerID: int, description):
    #     self.__main_picture_url = None
    #     self.__id = None
    #     self.__items_name = items_name
    #     self.__price = price
    #     self.__sellerID = sellerID
    #     self.__buyerID = None
    #     self.__post_date = datetime.datetime.now()
    #     self.__transaction_date = None
    #     self.__description = description


    # @property
    # def id(self):
    #     return self.__id
    #
    # @property
    # def items_name(self):
    #     return self.__items_name
    #
    # @items_name.setter
    # def items_name(self, item_name):
    #     self.__items_name = item_name
    #
    # @property
    # def price(self):
    #     return self.__price
    #
    # @price.setter
    # def price(self, price):
    #     self.__price = price
    #
    # @property
    # def sellerID(self):
    #     return self.__sellerID
    #
    # @sellerID.setter
    # def sellerID(self, sellerID):
    #     self.__sellerID = sellerID
    #
    # @property
    # def buyerID(self):
    #     return self.__buyerID
    #
    # @buyerID.setter
    # def buyerID(self, buyerID):
    #     self.__buyerID = buyerID
    #
    # @property
    # def post_date(self):
    #     return self.__post_date
    #
    # @post_date.setter
    # def post_date(self, value):
    #     self.__post_date = value
    #
    # @property
    # def transaction_date(self):
    #     return self.__transaction_date
    #
    # @transaction_date.setter
    # def transaction_date(self, value):
    #     self.__transaction_date = value
    #
    # @property
    # def description(self):
    #     return self.__description
    #
    # @description.setter
    # def description(self, value):
    #     self.__description = value
    #
    # @property
    # def main_picture_url(self):
    #     return self.__main_picture_url
    #
    # @main_picture_url.setter
    # def main_picture_url(self, value):
    #     self.__main_picture_url = value



class Items_del(Base):
    __tablename__ = 'items_del'
    del_id = Column(Integer, primary_key=True)
    prev_id = Column(Integer)
    items_name = Column(String)
    price = Column(Float)
    sellerID = Column(Integer)
    buyerID = Column(Integer)
    post_date = Column(DateTime)
    transaction_date = Column(DateTime)
    main_picture_url = Column(String)
    description = Column(String)
    del_date = Column(DateTime)