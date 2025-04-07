from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, func

from libs.db import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.now, server_default=func.now())
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_date = Column(DateTime, nullable=True)
