from flask import Flask
import os
#from flask.ext.sqlalchemy import SQLAlchemy
import redis
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
from mongoengine import connect 

app = Flask(__name__)
store = RedisStore(redis.StrictRedis())

KVSessionExtension(store, app)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.environ['MATCHMAKING_SECRET_KEY']
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')

from flask_oauth import OAuth

oauth = OAuth()
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=os.environ['MATCHMAKING_FB_APP_KEY'],
    consumer_secret=os.environ['MATCHMAKING_FB_APP_SECRET'],
    request_token_params={'scope': ['email', 'public_profile','user_friends','friends_education_history','friends_relationships']}
)

#db = SQLAlchemy(app)
connect('matches')


from app import views

