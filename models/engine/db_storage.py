#!/usr/bin/python3
'''database storage engine'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
from os import getenv

if getenv('HBNB_TYPE_STORAGE') == 'db':
    from models.place import place_amenity

classes = {"User": User, "State": State, "City": City,
           "Amenity": Amenity, "Place": Place, "Review": Review}


class DBStorage:
    '''db storage engine for mysql storage'''
    __engine = None
    __session = None

    def __init__(self):
        '''new db init'''
        HBNB_MYSQL_USER = getenv('HBNB_MYSQL_USER')
        HBNB_MYSQL_PWD = getenv('HBNB_MYSQL_PWD')
        HBNB_MYSQL_HOST = getenv('HBNB_MYSQL_HOST')
        HBNB_MYSQL_DB = getenv('HBNB_MYSQL_DB')
        HBNB_ENV = getenv('HBNB_ENV')
        self.__engine = create_engine(
            'mysql+mysqldb://{}:{}@{}/{}'.format(
                                           HBNB_MYSQL_USER,
                                           HBNB_MYSQL_PWD,
                                           HBNB_MYSQL_HOST,
                                           HBNB_MYSQL_DB
                                       ), pool_pre_ping=True)

        if HBNB_ENV == 'test':
            Base.metadata.drop_all(self.__engine)

        if HBNB_TYPE_STORAGE == 'db':
            Base.metadata.create_all(self.__engine)
            session_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
            self.__session = scoped_session(session_factory)()
        else:
            self.__engine = None
            self.__session = None
            self.file_storage = FileStorage()
            self.file_storage.reload()

    def all(self, cls=None):
        '''returns the dictionary in the current session'''
        dct = {}
        if cls is None:
            for c in classes.values():
                objs = self.__session.query(c).all()
                for obj in objs:
                    key = obj.__class__.__name__ + '.' + obj.id
                    dct[key] = obj
        else:
            objs = self.__session.query(cls).all()
            for obj in objs:
                key = obj.__class__.__name__ + '.' + obj.id
                dct[key] = obj
        return dct

    def new(self, obj):
        '''add an obj to the current db session'''
        if obj is not None:
            try:
                self.__session.add(obj)
                self.__session.flush()
                self.__session.refresh(obj)
            except Exception as ex:
                self.__session.rollback()
                raise ex

    def save(self):
        '''commit any change in the current db session'''
        self.__session.commit()

    def delete(self, obj=None):
        ''' deletes from the the obj in the current session
            if it's not None
        '''
        if obj is not None:
            self.__session.query(type(obj)).filter(
                type(obj).id == obj.id).delete()

    def reload(self):
        '''reload the database'''
        Base.metadata.create_all(self.__engine)
        session_factory = sessionmaker(bind=self.__engine,
                                       expire_on_commit=False)
        self.__session = scoped_session(session_factory)()

    def close(self):
        """ends the current SQLAlchemy session"""
        self.__session.close()
        
