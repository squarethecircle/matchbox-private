from flask import render_template,session,redirect,url_for,request,jsonify
from app import app, models, facebook
from models import User, Match
from random import randint
import json

blacklist = [1598222289,1389627032,100007479487216,100009034776491,100005656264666,100005208426975]

@app.route('/match',methods=['GET'])
def match():
	if session.get('facebook_token') is None:
		return redirect('/login?next=%2Fmatch')
# Here, we query for the user's friends list and each of their names, user ids, relationship statuses, and gender, taking only the data 
# for friends who have Yale in their education history or their affiliations. 
	if session.get('fixedfriends') is None:
		session['fixedfriends'] = facebook.get('fql?q=SELECT%20name%2Cuid%2Crelationship_status%2Csex%20FROM%20user%20WHERE%20uid%20IN'
			'%20(SELECT%20uid1%20FROM%20friend%20WHERE%20uid2%3Dme())%20and%20(%27Yale%20University%27%20in%20education%20or%20%27Yale'
			'%27%20in%20affiliations)').data['data']
	male_friends = []
	female_friends = []
# Most_upvoted refers to matches with many affirmative responses. Most_voted refers to matches with many responses of any kind.
	most_upvoted_matches_ids = []
	most_upvoted_matches = []
# Filtering out friends in relationships and on our blacklist and sorting them by gender and whether they are a close friend.
	for friend in session['fixedfriends']:
		if friend['sex'] == 'male' and friend['relationship_status'] != 'In a relationship' and friend['uid'] not in blacklist:
			male_friends.append(friend)
		elif friend['sex'] == 'female' and friend['relationship_status'] != 'In a relationship' and friend['uid'] not in blacklist:
			female_friends.append(friend)
	male_friends_ids = []
	female_friends_ids = []
	for friend in male_friends:
		male_friends_ids.append(friend['uid'])
	for friend in female_friends:
		female_friends_ids.append(friend['uid'])
# For the matches in our database where the user is friends with both parties, we sort out matches based on their number of upvotes and total votes.
	for match in Match.objects:
		if int(match.friends[0]) in male_friends_ids and int(match.friends[1]) in female_friends_ids:
			if match.num_matchers > 1:
				most_upvoted_matches_ids.append((int(match.friends[0]),int(match.friends[1])))
# Using the id lists to filter the database matches into the appropriate categories. Also making sure that if the user has seen a match, it is not added.
	user_obj = User.objects(fbid=session['fbid']).first()
	for i in range(0, len(most_upvoted_matches_ids)):
		for malefriend in male_friends:
			if malefriend['uid'] == most_upvoted_matches_ids[i][0]:
				for femalefriend in female_friends:
					if femalefriend['uid'] == most_upvoted_matches_ids[i][1]:
						if str((malefriend['uid'],femalefriend['uid'])) not in user_obj.seen_top_matches:
							most_upvoted_matches.append((malefriend,femalefriend))
						break
				break		
# Session is a global dictionary that we use to pass around relevant data between functions.
	session['male_friends'] = male_friends
	session['female_friends'] = female_friends
	session['most_upvoted_matches'] = most_upvoted_matches
# We cache one match so that users never have to wait for a match to load. 
	match_pair = getWeightedMatch(user_obj)
	match_pair_cache = getWeightedMatch(user_obj)

	acceptpercentfloatcache = getPercent(match_pair_cache)
	if acceptpercentfloatcache == None:
		acceptpercentcache = "No Data"
		rejectpercentcache = "No Data"
	else:
		acceptpercentcache = str(acceptpercentfloatcache) + "%"
		rejectpercentcache = str(100-acceptpercentfloatcache) + "%"

	new_match={'boy':match_pair_cache[0]['name'],'girl':match_pair_cache[1]['name'],'boypp':getPhoto(match_pair_cache[0]['uid']),
				'girlpp':getPhoto(match_pair_cache[1]['uid']),'boyid':match_pair_cache[0]['uid'],
				'girlid':match_pair_cache[1]['uid'],'acceptpercent':acceptpercentcache,'rejectpercent':rejectpercentcache}
	return render_template('match.html',boy=match_pair[0]['name'], girl=match_pair[1]['name'],
			boypp=getPhoto(match_pair[0]['uid']),girlpp=getPhoto(match_pair[1]['uid']),
			boyid=match_pair[0]['uid'],girlid=match_pair[1]['uid'],acceptpercent="",rejectpercent="",
			match_cache=json.dumps(new_match))

@app.route('/match',methods=['POST'])
def acceptMatch():
	friend1 = request.form.get('friend1')
	friend2 = request.form.get('friend2')
	friend1name = request.form.get('friend1name')
	friend2name = request.form.get('friend2name')
# We store the data from the match in our database, recording names of the people matched, their fbids, the fbids and names of the matchers 
# and the nonmatchers, and the total number of unique matchers and nonmatchers.
	if request.form.get('result') == 'accept':
		query = Match.objects(friends__all=[friend1,friend2]).first()
		if query == None:
			new_match = Match(friends=[friend1,friend2],friend_names=[friend1name,friend2name],matchers=[session['fbid']],num_matchers=1,
				matcher_names=[session['name']],nonmatchers=[],num_nonmatchers=0,nonmatcher_names=[],confirmed=False).save()	
			query = new_match
		elif session['fbid'] not in query.matchers:
			query.matchers.append(session['fbid'])
			query.matcher_names.append(session['name'])
			query.num_matchers += 1
			query.save()
	elif request.form.get('result') == 'reject':
		query = Match.objects(friends__all=[friend1,friend2]).first()
		if query == None:
			new_match = Match(friends=[friend1,friend2],friend_names=[friend1name,friend2name],matchers=[],num_matchers=0,matcher_names=[],
				nonmatchers=[session['fbid']],num_nonmatchers=1,nonmatcher_names=[session['name']],confirmed=False).save()
			query = new_match		
		elif session['fbid'] not in query.nonmatchers:
			query.nonmatchers.append(session['fbid'])
			query.nonmatcher_names.append(session['name'])
			query.num_nonmatchers += 1
			query.save()

	user_obj = User.objects(fbid=session['fbid']).first()
	user_obj.num_submitted += 1
	user_obj.save()

	match_pair = getWeightedMatch(user_obj)

	acceptpercentfloat = getPercent(match_pair)
	if acceptpercentfloat == None:
		acceptpercent = "No Data"
		rejectpercent = "No Data"
	else:
		acceptpercent = str(acceptpercentfloat) + "%"
		rejectpercent = str(100-acceptpercentfloat) + "%"

	new_match={'boy':match_pair[0]['name'],'girl':match_pair[1]['name'],'boypp':getPhoto(match_pair[0]['uid']),
				'girlpp':getPhoto(match_pair[1]['uid']),'boyid':match_pair[0]['uid'],
				'girlid':match_pair[1]['uid'],'acceptpercent':acceptpercent,'rejectpercent':rejectpercent}
	return jsonify(new_match)

@app.route('/jsonifyMatch')
def jsonifyMatch():
	user_obj = User.objects(fbid=session['fbid']).first()
	match_pair = getWeightedMatch(user_obj)
	new_match={'boy':match_pair[0]['name'],'girl':match_pair[1]['name'],'boypp':getPhoto(match_pair[0]['uid']),
				'girlpp':getPhoto(match_pair[1]['uid']),'boyid':match_pair[0]['uid'],
				'girlid':match_pair[1]['uid']}	
	return jsonify(new_match)

# A function to query an appropriately sized and croped profile picture from facebook, that takes the user fbid as a parameter.
def getPhoto(uid):
	if app.config['TESTING'] == True:
		return "testing time - test photo here"
	photo = facebook.get('fql?q=SELECT%20pic_crop%20from%20profile%20where%20id%3D'+str(uid)).data['data'][0]['pic_crop']
	return photo['uri']

# A function that uses weighted percentages to return a semi-random match to display to our user.
def getWeightedMatch(user_obj):
	x = randint(1,4)
	if x == 1 and session['most_upvoted_matches']:
		match_pair = (session['most_upvoted_matches'][randint(0,len(session['most_upvoted_matches'])-1)])
		session['most_upvoted_matches'].remove(match_pair)
		user_obj.seen_top_matches.append(str((match_pair[0]['uid'],match_pair[1]['uid'])))
		user_obj.save()
	else:
		match_pair = (session['male_friends'][randint(0,len(session['male_friends'])-1)],
			session['female_friends'][randint(0,len(session['female_friends'])-1)])
	session.modified=True
	return match_pair

# A function to query the percent upvoted for any given match.
def getPercent(match_pair):
	percentquery = Match.objects(friends__all=[str(match_pair[0]['uid']),str(match_pair[1]['uid'])]).first()
	if percentquery == None:
		acceptpercentfloat = None
	else:
		acceptpercentfloat = int(float(percentquery.num_matchers)/(percentquery.num_nonmatchers+percentquery.num_matchers) * 100)
	return acceptpercentfloat

