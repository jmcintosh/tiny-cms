
import jwt
import re
from functools import wraps
from flask_restplus import reqparse
from werkzeug.exceptions import BadRequest
from flask import make_response

from tiny_cms.config import config

# Helper, creates new bad request error
def bad_request(message):
    e = BadRequest(message)
    e.data = { 'error': message }
    return e

# JWT Auth decorator
def requires_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('Authorization', type=str, location='headers', required=True, help='Authorization header is required.')
        args = parser.parse_args()
        
        # Parse header
        search = re.search(r"^Bearer\s(.*)", args.Authorization)
        if search is None:
            raise bad_request('Invalid token')

        encoded = search.groups()[0]

        # Attempt to decode JWT
        try:
            decoded = jwt.decode(encoded, config.get('token', 'secret'), algorithms=['HS256'])
        except jwt.InvalidTokenError:
            raise bad_request('Invalid token')

        # Pass token to decorated function
        kwargs['token'] = decoded
        
        return f(*args, **kwargs)
    return decorated

# CORS decorator

def cors(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    return decorated
        
