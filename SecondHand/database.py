from sqlalchemy.orm import sessionmaker, clear_mappers, scoped_session, class_mapper
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
# from .orm import metadata, map_model_to_tables
from .model import Items, Base

def connect_database(app):
    database_uri = app.config.get('SECONDHAND_SQLALCHEMY_DATABASE_URI', 'sqlite:///SecondHand.db')
    database_echo = app.config.get('SECONDHAND_SQLALCHEMY_ECHO', False)
    database_engine = create_engine(database_uri, connect_args={"check_same_thread": False}, poolclass=NullPool,
                                    echo=database_echo)
    session_factory = sessionmaker(autocommit=False, autoflush=True, bind=database_engine)
    if len(database_engine.table_names()) == 0:
        print("REPOPULATING DATABASE for SecondHand Plugin ...")
        # clear_mappers()
        Base.metadata.create_all(database_engine)
        # for table in reversed(Base.metadata.sorted_tables):  # Remove any data from the tables.
        #     database_engine.execute(table.delete())
        # Generate mappings that map domain model classes to the database tables.
        # map_model_to_tables()
        print("REPOPULATING DATABASE for SecondHand Plugin ... FINISHED")
    # else:
        # Solely generate mappings that map domain model classes to the database tables.
        # map_model_to_tables()
    return session_factory
