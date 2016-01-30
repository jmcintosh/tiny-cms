# code goes here

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask
from flask import jsonify

from models.base import Base
from models.user import User

# Connect to database and create a new session

engine = create_engine('postgresql://danquinn@localhost/tiny_cms', echo=True)

# Bootstrap database

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Create new instance of flask application

app = Flask(__name__)

# Route definitions

@app.route('/api/users')
def hello():
    users = session.query(User)
    return jsonify(results=[user.serialize for user in users.all()])