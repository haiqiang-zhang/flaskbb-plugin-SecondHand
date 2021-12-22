from sqlalchemy.orm import sessionmaker, clear_mappers, scoped_session, class_mapper
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from .model import Items, Base, orderStatus

def connect_database(app):
    database_uri = app.config.get('SECONDHAND_SQLALCHEMY_DATABASE_URI', 'sqlite:///SecondHand.db')
    database_echo = app.config.get('SECONDHAND_SQLALCHEMY_ECHO', False)
    database_engine = create_engine(database_uri, connect_args={"check_same_thread": False}, poolclass=NullPool,
                                    echo=database_echo)
    session_factory = sessionmaker(autocommit=False, autoflush=True, bind=database_engine)
    if len(database_engine.table_names()) == 0:
        print("REPOPULATING DATABASE for SecondHand Plugin ...")
        Base.metadata.create_all(database_engine)
        session = session_factory()
        orderStatusAll = [orderStatus(id=1, StatusName="On-Sale"),
                          orderStatus(id=2, StatusName="On-Transaction"),
                          orderStatus(id=3, StatusName="Buyer-Cancel"),
                          orderStatus(id=4, StatusName="Confirmed"),
                          orderStatus(id=5, StatusName="Success")]
        session.add_all(orderStatusAll)
        session.commit()
        print("REPOPULATING DATABASE for SecondHand Plugin ... FINISHED")
    return session_factory
