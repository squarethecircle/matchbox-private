from flask import render_template,session,redirect,url_for,request,flash,jsonify,Response
from app import app,models,facebook
from models import User
import requests
from chat import *
from sockets import *
from matches import *


@facebook.tokengetter
def get_facebook_token(token=None):
	return session.get('facebook_token')

@app.route('/login')
def login():
	return facebook.authorize(callback = url_for('oauth_authorized',next=request.args.get('next') or request.referrer,_external=True))

@app.route('/logout')
def logout():
	session.pop('facebook_token')
	return redirect('/index')

# Get facebook authorization from the user and collect and store some simple user data.
@app.route('/oauth_authorized')
@facebook.authorized_handler
def oauth_authorized(resp):
	next_url = request.args.get('next') or url_for('index')
	if resp is None:
		flash(u'You denied the request to sign in.')
		return redirect(next_url)
	session['facebook_token'] = (resp['access_token'], resp['expires'])
	basic_info = facebook.get('me?fields=id,name').data
	if 'fbid' in session and session['fbid'] != basic_info['id']:
		session.pop('fixedfriends',None)
	session['fbid'] = basic_info['id']
	session['name'] = basic_info['name']
	query = User.objects(fbid=session['fbid']).first()
	if query == None:
		new_user = User(fbid=session['fbid'],name=session['name'],seen_top_matches=[],num_submitted=0)
		new_user.save()	
	send_username(basic_info['name'])
	return redirect(next_url)

@app.route('/')
@app.route('/index')
def index():
	return render_template('landingpage.html')



def send_username(name):
	rand_name=getRandomName()
	return requests.post(
		"https://api.mailgun.net/v2/matchboxapp.me/messages",
		auth=("api", app.config['MAILGUN_KEY']),
		data={"from": rand_name.title() + " <"+rand_name.split()[0]+rand_name.split()[1]+"@matchboxapp.me>",
			"to": ["Matchbox Team", "team@matchboxapp.me"],
			"subject": "People like you!",
			"text": name+" just signed on to Matchbox!"})

