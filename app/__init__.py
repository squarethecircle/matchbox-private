from flask import Flask
import os
import redis
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
from mongoengine import connect 

app = Flask(__name__)
store = RedisStore(redis.StrictRedis())

KVSessionExtension(store, app)

app.config['SECRET_KEY'] = os.environ['MATCHMAKING_SECRET_KEY']


if os.environ['MATCHMAKING_STATUS'] == 'DEBUG':
	connect('matches')
else:
	connect(os.environ['MONGODB_PROD'])

from flask_oauth import OAuth
import os
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


from app import views
