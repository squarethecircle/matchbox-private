from flask import render_template,session,redirect,url_for,request,flash,jsonify
from app import app,models,facebook

@facebook.tokengetter
def get_facebook_token(token=None):
    return session.get('facebook_token')


@app.route('/login')
def login():
	return facebook.authorize(callback = 'http://localhost:5000/oauth_authorized')

@app.route('/oauth_authorized')
@facebook.authorized_handler
def oauth_authorized(resp):
	next_url = request.args.get('next') or url_for('index')
	if resp is None:
		flash(u'You denied the request to sign in.')
		return redirect(next_url)
	session['facebook_token'] = (resp['access_token'], resp['expires'])
	flash('You were signed in as %s' % resp['access_token'])
	return redirect(next_url)

@app.route('/')
@app.route('/index')
def index():
	return "Hello World"
@app.route('/match')
def match():
	#resp = facebook.get('me/friends?fields=name,id,education')
	resp = facebook.get('fql?q=SELECT name,uid,pic_big,relationship_status,sex FROM user WHERE uid IN (SELECT uid1 FROM friend WHERE uid2=me()) and ('Yale University' in education or 'Yale' in affiliations)')
	if resp.status == 200:
		friends = resp.data
	return jsonify(friends)

