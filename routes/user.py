
import re
import bcrypt
import jwt
from sqlalchemy.exc import IntegrityError
from flask_restplus import Resource, fields, reqparse
from werkzeug.exceptions import BadRequest

from tiny_cms.config import config
from models.user import User
from decorators import requires_token

# Helper, creates new bad request error
def bad_request(message):
    e = BadRequest(message)
    e.data = { 'error': message }
    return e

# Helper, generates a token for a user
def generate_token(user):
 
    #Generate a new JWT containing user info which can be used to authenticate future api calls
    return jwt.encode(
      { 'username': user.username, 'email': user.email, 'id': user.id },
      config.get('token', 'secret'),
      algorithm='HS256'
    )

'''
Flask Restplus definitions
api - flask_restplus api instance
session - sqlalchemy session instance
'''
def initialize(api, session):

    #Namespace
    ns = api.namespace('users', description='User operations')

    #User model
    user = api.model('User', {
        'id': fields.Integer(readOnly=True, description='User unique identifier'),
        'username': fields.String(description='Unique username'),
        'email': fields.String(description='Unique email')
    })

    #List operations
    @ns.route('/')
    class UserResourceList(Resource):

        #List users and create new ones
        @api.doc('list_users')
        @api.marshal_list_with(user)
        def get(self):

            '''List all users'''
            users = session.query(User).all()
            return [ user.serialize for user in users ]

        @api.doc('create_user')
        def post(self):

            '''Create a new user'''
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, location='json', required=True, help='Username is required and must be unique.')
            parser.add_argument('email', type=str, location='json', required=True, help='Email address is required and must be unique.')
            parser.add_argument('verify_email', type=str, location='json', required=True, help='Email confirmation is required.')
            parser.add_argument('password', type=str, location='json', required=True, help='Password is a required field.')
            args = parser.parse_args()
            
            #Validate email
            if not re.match(r"[^@]+@[^@]+\.[^@]+", args.email):
                raise bad_request('Invalid email address')
            
            #Verify emails match
            if (args.email != args.verify_email):
                raise bad_request('Emails do not match')

            #Encrypt password
            password = bcrypt.hashpw(args.password, bcrypt.gensalt()) 

            #Create a new instance of User and attempt to add it to db
            user = User(username=args.username, email=args.email, password=password)

            try:
                session.add(user)
                session.commit()
            except IntegrityError, exc:
                if 'duplicate' in exc.message:
                    session.rollback()
                    raise bad_request('Username or email already exists')

            # Return a new token
            return generate_token(user)

    # User login
    @ns.route('/login')
    class UserResourceLogin(Resource):

        #Checks credentials and issues a token
        @api.doc('login_user')
        @api.doc(params={'username': 'Username', 'password': 'Password'})
        def post(self):

            '''Check credentials and issue token'''
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, location='json', required=True, help='Must supply username.')
            parser.add_argument('password', type=str, location='json', required=True, help='Must supply password.')
            args = parser.parse_args()

            # Find an existing user
            user = session.query(User).filter_by(username = args.username).first()

            if user is None:
                raise bad_request('Incorrect username or password')

            #Check password
            if bcrypt.hashpw(args.password.encode('utf-8'), user.password.encode('utf-8')) != user.password:
                raise bad_request('Incorrect username or password')

            # Return a new token
            return generate_token(user)

    # User get, update delete users
    @ns.route('/<user_id>')
    @api.response(404, 'User not found')
    @api.doc(params={'user_id': 'The user id' })
    class UserResource(Resource):
    
        # Gets a single user by id
        def get(self, user_id):
            
            # Find user
            user = session.query(User).filter_by(id = user_id).first()
            
            if user is None:
                api.abort(404, "user {} doesn't exist".format(user_id))
            
            return user.serialize

        @api.response(204, 'User deleted')
        @requires_token
        def delete(self, user_id, token):
        
            # Verify same user
            if (token['id'] != user_id):
                api.abort(403, 'You cannot delete this user')
            
            # Delete user
            try:
                session.delete(user)
                session.commit()
            except IntegrityError, exc:
                if 'duplicate' in exc.message:
                    session.rollback()
                    raise bad_request('Username or email already exists')