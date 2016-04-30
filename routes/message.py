
from flask_restplus import Resource, fields, reqparse
from werkzeug.exceptions import BadRequest

from models.message import Message
from decorators import requires_token

# Helper, creates new bad request error
def bad_request(message):
    e = BadRequest(message)
    e.data = { 'error': message }
    return e

'''Flask restplus definitions'''
def initialize(api, session):
    
    # Namespace
    ns = api.namespace('messages', description='Message operations')
    
    # Message model
    message = api.model('Message', {
        'id': fields.Integer(readOnly=True, description='Message unique identifier'),
        'user_id': fields.Integer(readOnly=True, description='User id'),
        'content': fields.String(description='Message content, 1000 characters max')
    })
    
    # List operations
    @ns.route('/')
    class MessageList(Resource):
    
        # List messages and create new ones
        @api.doc('list_messages')
        @api.marshal_list_with(message)
        def get(self):
        
            '''List all messages'''
            messages = session.query(Message).all()
            return [message.serialize for message in messages]
       
        @requires_token
        def post(self, token):
          
            '''Create a new message'''
            parser = reqparse.RequestParser()
            parser.add_argument('content', type=str, location='json', required=True, help='Content is a required field.')
            args = parser.parse_args()
            
            #Validate content
            if len(args.content) == 0:
                raise bad_request('Message cannot be empty')

            #Create a new instance of Content and attempt to add it to db
            print token
            message = Message(content=args.content, user_id=token['id'])

            try:
                session.add(message)
                session.commit()
            except IntegrityError, exc:
                session.rollback()
                raise bad_request('Cannot create message')

            return { 'message': 'Created message' }
            