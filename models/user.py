
from sqlalchemy import Column, Integer, Boolean, String, UniqueConstraint
from base import Base

# User sqlalchemy object
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    email_verified = Column(Boolean, default=False)
    password = Column(String, nullable=False)
    
    @property
    def serialize(self):
        return {
          'id': self.id,
          'username': self.username,
          'email': self.email
        }
