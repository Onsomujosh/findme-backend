#!/usr/bin/python3
""" State Module for HBNB project """
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String
from flask_sqlalchemy import SQLAlchemy
from app import ds


class Amenity(BaseModel, Base):
    '''amenity class'''
    __tablename__ = 'amenities'
    name = ds.Column(String(128), nullable=False)
