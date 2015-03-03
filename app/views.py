from flask import render_template,session,redirect,url_for,request,flash,jsonify
from app import app,models,facebook
from random import randint

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
	return redirect('/index')

@app.route('/')
@app.route('/index')
def index():
	return "Hello World"
@app.route('/match')
def match():
	#resp = facebook.get('me/friends?fields=name,id,education')
	if session.get('friends') is None:
		session['friends'] = facebook.get('fql?q=SELECT%20name%2Cuid%2Cpic_big%2Crelationship_status%2Csex%20FROM%20user%20WHERE%20uid%20IN%20(SELECT%20uid1%20FROM%20friend%20WHERE%20uid2%3Dme())%20and%20(%27Yale%20University%27%20in%20education%20or%20%27Yale%27%20in%20affiliations)').data['data']
	male_friends = []
	female_friends = []
	for friend in session['friends']:
		if friend['sex'] == 'male' and friend['relationship_status'] != 'In a relationship':
			male_friends.append(friend)
		elif friend['sex'] == 'female' and friend['relationship_status'] != 'In a relationship':
			female_friends.append(friend)
	match_pair = (male_friends[randint(0,len(male_friends)-1)],female_friends[randint(0,len(female_friends)-1)])
	#return str(match_pair)
	return render_template('layout.html',boy=match_pair[0]['name'], girl=match_pair[1]['name'],boypp=match_pair[0]['pic_big'],girlpp=match_pair[1]['pic_big'])

