
from sqlalchemy import Column, ForeignKey, Integer, String
from base import Base

# Message sqlalchemy object
class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(String(length=1000), nullable=True)
    
    @property
    def serialize(self):
        return {
          'id': self.id,
          'user_id': self.user_id,
          'content': self.content
        }
