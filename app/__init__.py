from flask import Flask
import os
import redis
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
from mongoengine import connect 
import urlparse

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['MATCHMAKING_SECRET_KEY']


if os.environ['MATCHMAKING_STATUS'] == 'DEBUG':
	app.config['APP_DOMAIN'] = 'http://localhost:5000/'
	connect('matches')
	app.config['DEBUG'] = True
	store = RedisStore(redis.StrictRedis())
	KVSessionExtension(store, app)

else:
	app.config['APP_DOMAIN'] = 'http://www.matchboxapp.me/'
	connect('matches',host=os.environ['MONGOLAB_URI'])
	url = urlparse.urlparse(os.environ['REDISCLOUD_URL'])
	store = RedisStore(redis.StrictRedis(host=url.hostname, port=url.port, password=url.password))
	KVSessionExtension(store, app)
	#app.config['PROPAGATE_EXCEPTIONS'] = True


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
    request_token_params={'scope': 'email,public_profile,user_friends,friends_education_history,friends_relationships'}
)
app.config['MAILGUN_KEY']=os.environ['MATCHMAKING_MAILGUN_KEY']

from app import views
