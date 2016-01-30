# code goes here

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask
from flask_restplus import Api

from resources.base import Base
import resources.user as user

# Connect to database and create a new session

engine = create_engine('postgresql://danquinn@localhost/tiny_cms', echo=True)

# Bootstrap database

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Create new instance of flask application

app = Flask(__name__)
api = Api(app, version='1.0', title='Tiny Cms API', description='CRUD content')

# Initialize resources

user.initialize(api, session)
