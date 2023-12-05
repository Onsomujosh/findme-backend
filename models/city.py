#!/usr/bin/python3
""" City Module for HBNB project """
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


class City(BaseModel, Base):
    """ state ID and name """
    __tablename__ = 'cities'

    name = ds.Column(String(128), nullable=False)
    state_id = ds.Column(String(60), ForeignKey('states.id'), nullable=False)
    places = ds.relationship('Place', backref='cities',
                              cascade='all, delete, delete-orphan')

    @classmethod
    def all(cls):
    """Retrieve all city instances"""
        from models import storage
        return [city for city in storage.all(City).values()]
