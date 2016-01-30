
from base import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    
    @property
    def serialize(self):
        return {
          'id': self.id,
          'username': self.username,
          'email': self.email
        }