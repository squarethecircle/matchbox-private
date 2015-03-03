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
	if session.get('friends') = None:
		session['friends'] = facebook.get('fql?q=SELECT%20name%2Cuid%2Cpic_big%2Crelationship_status%2Csex%20FROM%20user%20WHERE%20uid%20IN%20(SELECT%20uid1%20FROM%20friend%20WHERE%20uid2%3Dme())%20and%20(%27Yale%20University%27%20in%20education%20or%20%27Yale%27%20in%20affiliations)')
	return jsonify(session['friends'])

