
import re
from base import Base
from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from flask_restplus import Resource, fields, reqparse
from werkzeug.exceptions import BadRequest

# User sqlalchemy object

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    
    @property
    def serialize(self):
        return {
          'id': self.id,
          'username': self.username,
          'email': self.email
        }

# Flask Restplus definitions

def initialize(api, session):

    ns = api.namespace('users', description='User operations')

    user = api.model('User', {
      'id': fields.Integer(readOnly=True, description='User unique identifier'),
      'username': fields.String(description='Unique username'),
      'email': fields.String(description='Unique email')
    })

    @ns.route('/')
    class UserList(Resource):
        '''List users and create new ones'''
        @api.doc('list_users')
        @api.marshal_list_with(user)
        def get(self):
            '''List all users'''
            users = session.query(User).all()
            return [ user.serialize for user in users ]

        '''Creates a new user'''
        @api.doc('create_user')
        def post(self):
            '''Create a new user'''
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, location='json', required=True, help='Unique username. This is a required field.')
            parser.add_argument('email', type=str, location='json', required=True, help='Unique email address. This is a required field.')
            parser.add_argument('verify_email', type=str, location='json', required=True, help='Email verification, must match email. This is a required field.')
            parser.add_argument('password', type=str, location='json', required=True, help='Password, this is a required field')
            args = parser.parse_args()
            
            if not re.match(r"[^@]+@[^@]+\.[^@]+", args.email):
                message = 'Invalid email address'
                e = BadRequest(message)
                e.data = { 'error': message }
                raise e
            
            if (args.email != args.verify_email):
                message = 'Emails do not match'
                e = BadRequest(message)
                e.data = { 'error': message }
                raise e
            
            user = User(username=args.username, email=args.email, password=args.password)

            try:
                session.add(user)
                session.commit()
            except IntegrityError, exc:
                if 'duplicate' in exc.message:
                  message = 'Username or email already exists'
                  e = BadRequest(message)
                  e.data = { 'error': message }
                  raise e
            
            return user.serialize
