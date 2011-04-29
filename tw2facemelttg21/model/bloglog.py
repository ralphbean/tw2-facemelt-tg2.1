# -*- coding: utf-8 -*-
""" Logs of Bob Loblaw's Law Blog """

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.orm import relation, backref

from datetime import datetime

from tw2facemelttg21.model import DeclarativeBase, metadata, DBSession


class ServerHit(DeclarativeBase):
    __tablename__ = 'server_hit'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    
    remote_addr = Column(Unicode(15), nullable=False)

    path_info = Column(Unicode(1024), nullable=False)
    query_string = Column(Unicode(1024), nullable=False)
