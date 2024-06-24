from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import anthropic
import google.generativeai as gemini
from openai import OpenAI
from dotenv import load_dotenv
import os

# load api keys and database uri
load_dotenv()

antClient = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
gemini.configure(api_key=os.getenv('GEMINI_API_KEY'))
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


app= Flask(__name__)
CORS(app, resources={
    r"/*": {"origins": "http://localhost:5173"}
}, supports_credentials=True)
app.secret_key = "temp key"

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from app.models import User, Hotel, Room, Booking, Amenities

from app.routes import api
app.register_blueprint(api)

