from flask import render_template,session,redirect,url_for,request,flash,jsonify
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from app import app,models,facebook
from random import randint
from models import Match, User, Chat, Message,RevealChoice
import json
import requests
import datetime, random

blacklist = [1598222289,1389627032,100007479487216,100009034776491,100005656264666,100005208426975]

@app.route('/chat')
def chat():
	return render_template('chat.html')

@app.route('/testarooney')
def NewMessage():
	user = session['fbid']
	will = '629263828'
	msg = request.args.get('msg')
	if request.args.get('r') == 1:
		new_msg = Message(sender=will,recipient=user,text=msg)
	new_msg = Message(sender=user,recipient=will,text=msg)
	chat = Chat.objects(pair=[user,will]).first()
	if chat is None:
		chat=createChat(user,will)
		chat.save()
	chat.update(add_to_set__messages=[new_msg])
	return msg

def createChat(user1, user2):
	reveal1 = RevealChoice(user=user1)
	reveal2 = RevealChoice(user=user2)
	new_chat = Chat(pair=[user1,user2],reveals=[reveal1,reveal2])
	return new_chat

@app.route('/retrieveMessages')
def getMessages():
	user = session['fbid']
	other = request.args.get('other')
	messages = Chat.objects(pair__all=[user,other]).first().messages
	json_messages = []
	for message in messages:
		json_message = {'sender':message.sender,'recipient':message.recipient,'text':message.text,'sent_time':message.sent_time.strftime('%m/%d/%Y %I:%M:%S %p')}
		json_messages.append(json_message)
	return jsonify({"messages":json_messages})

@facebook.tokengetter
def get_facebook_token(token=None):
    return session.get('facebook_token')

@app.route('/login')
def login():
	return facebook.authorize(callback = app.config['APP_DOMAIN']+'oauth_authorized')

@app.route('/logout')
def logout():
	session.pop('facebook_token')
	return redirect('/index')

#Get facebook authorization from the user and collect and store some simple user data.
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
	return redirect('/match')

@app.route('/')
@app.route('/index')
def index():
	return render_template('landingpage.html')

@app.route('/match',methods=['GET'])
def match():
	if session.get('facebook_token') is None:
		return redirect('/index')
#Here, we query for the user's friends list and each of their names, user ids, relationship statuses, and gender, taking only the data for friends who have Yale in their education history or their affiliations. 
	if session.get('fixedfriends') is None:
		session['fixedfriends'] = facebook.get('fql?q=SELECT%20name%2Cuid%2Crelationship_status%2Csex%20FROM%20user%20WHERE%20uid%20IN%20(SELECT%20uid1%20FROM%20friend%20WHERE%20uid2%3Dme())%20and%20(%27Yale%20University%27%20in%20education%20or%20%27Yale%27%20in%20affiliations)').data['data']
	male_friends = []
	female_friends = []
	top_matches = []
#Our initial test group consists of 20-30 friends in Berkeley College. In order to model the same experience our future users will have, without any preexisting data, we have made a list of all of their facebook ids, stored under lifestyle ids, which serves as a list of their close friends. This list is incorporated into our algorithm for showing matches.
	lifestyle_male_friends = []
	lifestyle_female_friends = []
	lifestyle_ids = [100000117930891, 1673808394, 749512978, 629263828, 1120293045, 100000279378280, 1646941022, 644659874, 707859779, 774168034, 821596896, 1235948517, 1306399238, 1293191998, 1391794445, 1471153226, 1522524524, 1666913902, 1577529446, 1598222289, 100004191697613, 100000359149448, 100000892201552, 100001288758840]
	top_matches_ids = [(1375642201, 1646941022), (705579939, 100003888319326), (644659874, 1425476801), (707859779, 1321417892), (707859779, 100005920514441), (644659874, 100005920514441), (1375642201, 1522524524), (1306399238, 100000742350322), (1293191998, 100000742350322), (1235948517, 100004191697613), (100000279378280, 1397434942),  (100000486251970, 1490615349),  (100004797271381, 100000163821701), (100000117930891, 1391794445), (100000117930891, 1471153226), (821596896, 1471153226), (774168034,	1397434942), (100000117930891, 1321417892), (100000279378280, 1490615349), (821596896, 1391794445), (774168034, 100001663293430), (100000279378280, 1321417892), (774168034, 100000742350322), (1293191998, 1321417892), (1293191998, 1471153226), (100000279378280, 100000163821701), (1293191998, 1391794445), (100004797271381, 1425476801), (100000892201552, 1425476801), (100000892201552, 1522524524), (100000279378280, 1248783721), (100002804284636, 1248783721)]
#Most_upvoted refers to matches with many affirmative responses. Most_voted refers to matches with many responses of any kind.
	most_upvoted_matches_ids = []
	most_upvoted_matches = []
	most_voted_matches_ids = []
	most_voted_matches = []
#Filtering out friends in relationships and on our blacklist and sorting them by gender and whether they are a close friend.
	for friend in session['fixedfriends']:
		if friend['sex'] == 'male' and friend['relationship_status'] != 'In a relationship':
			if friend['uid'] in lifestyle_ids:
				lifestyle_male_friends.append(friend)
			if friend['uid'] not in blacklist:
				male_friends.append(friend)
		elif friend['sex'] == 'female' and friend['relationship_status'] != 'In a relationship':
			if friend['uid'] in lifestyle_ids:
				lifestyle_female_friends.append(friend)
			if friend['uid'] not in blacklist:
				female_friends.append(friend)

	male_friends_ids = []
	female_friends_ids = []
	for friend in male_friends:
		male_friends_ids.append(friend['uid'])
	for friend in female_friends:
		female_friends_ids.append(friend['uid'])
#For the matches in our database where the user is friends with both parties, we sort out matches based on their number of upvotes and total votes.
	for match in Match.objects:
		if int(match.friends[0]) in male_friends_ids and int(match.friends[1]) in female_friends_ids:
			if match.num_matchers > 0:
				most_upvoted_matches_ids.append((int(match.friends[0]),int(match.friends[1])))
			if match.num_matchers + match.num_nonmatchers > 1:
				most_voted_matches_ids.append((int(match.friends[0]),int(match.friends[1])))
#Using the id lists to filter the database matches into the appropriate categories. Also making sure that if the user has seen a match, it is not added.
	user_obj = User.objects(fbid=session['fbid']).first()
	for i in range(0, len(top_matches_ids)):
		for malefriend in male_friends:
			if malefriend['uid'] == top_matches_ids[i][0]:
				for femalefriend in female_friends:
					if femalefriend['uid'] == top_matches_ids[i][1]:
						if str((malefriend['uid'],femalefriend['uid'])) not in user_obj.seen_top_matches:
							top_matches.append((malefriend, femalefriend))
						break
				break
			if most_upvoted_matches_ids:
				if malefriend['uid'] == most_upvoted_matches_ids[i][0]:
					for femalefriend in female_friends:
						if femalefriend['uid'] == most_upvoted_matches_ids[i][1]:
							if str((malefriend['uid'],femalefriend['uid'])) not in user_obj.seen_top_matches:
								most_upvoted_matches.append((malefriend,femalefriend))
							break
					break
			if most_voted_matches_ids:
				if malefriend['uid'] == most_voted_matches_ids[i][0]:
					for femalefriend in female_friends:
						if femalefriend['uid'] == most_voted_matches_ids[i][1]:
							if str((malefriend['uid'],femalefriend['uid'])) not in user_obj.seen_top_matches:
								most_voted_matches.append((malefriend,femalefriend))
							break
					break			
#Session is a global dictionary that we use to pass around relevant data between functions.
	session['male_friends'] = male_friends
	session['female_friends'] = female_friends
	session['lifestyle_male_friends'] = lifestyle_male_friends
	session['lifestyle_female_friends'] = lifestyle_female_friends
	session['top_matches'] = top_matches
	session['most_upvoted_matches'] = most_upvoted_matches
	session['most_voted_matches'] = most_voted_matches
#We cache one match so that users never have to wait for a match to load. 
	match_pair = getWeightedMatch(user_obj)
	match_pair_cache = getWeightedMatch(user_obj)

	acceptpercentfloat = getPercent(match_pair)
	if acceptpercentfloat == None:
		acceptpercent = "No Data"
		rejectpercent = "No Data"
	else:
		acceptpercent = str(acceptpercentfloat) + "%"
		rejectpercent = str(100-acceptpercentfloat) + "%"

	new_match={'boy':match_pair_cache[0]['name'],'girl':match_pair_cache[1]['name'],'boypp':getPhoto(match_pair_cache[0]['uid']),
				'girlpp':getPhoto(match_pair_cache[1]['uid']),'boyid':match_pair_cache[0]['uid'],
				'girlid':match_pair_cache[1]['uid'],'acceptpercent':acceptpercent,'rejectpercent':rejectpercent}
	return render_template('match.html',boy=match_pair[0]['name'], girl=match_pair[1]['name'],
			boypp=getPhoto(match_pair[0]['uid']),girlpp=getPhoto(match_pair[1]['uid']),
			boyid=match_pair[0]['uid'],girlid=match_pair[1]['uid'],acceptpercent="",rejectpercent="",match_cache=json.dumps(new_match))

@app.route('/match',methods=['POST'])
def acceptMatch():
	friend1 = request.form.get('friend1')
	friend2 = request.form.get('friend2')
	friend1name = request.form.get('friend1name')
	friend2name = request.form.get('friend2name')
#We store the data from the match in our database, recording names of the people matched, their fbids, the fbids and names of the matchers and the nonmatchers, and the total number of unique matchers and nonmatchers.
	if request.form.get('result') == 'accept':
		query = Match.objects(friends__all=[friend1,friend2]).first()
		if query == None:
			new_match = Match(friends=[friend1,friend2],friend_names=[friend1name,friend2name],matchers=[session['fbid']],num_matchers=1,matcher_names=[session['name']],nonmatchers=[],num_nonmatchers=0,nonmatcher_names=[],confirmed=False).save()	
			query = new_match
		elif session['fbid'] not in query.matchers:
			query.matchers.append(session['fbid'])
			query.matcher_names.append(session['name'])
			query.num_matchers += 1
			query.save()
	elif request.form.get('result') == 'reject':
		query = Match.objects(friends__all=[friend1,friend2]).first()
		if query == None:
			new_match = Match(friends=[friend1,friend2],friend_names=[friend1name,friend2name],matchers=[],num_matchers=0,matcher_names=[],nonmatchers=[session['fbid']],num_nonmatchers=1,nonmatcher_names=[session['name']],confirmed=False).save()
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

#A function to query an appropriately sized and croped profile picture from facebook, that takes the user fbid as a parameter.
def getPhoto(uid):
	if app.config['TESTING'] == True:
		return "testing time - test photo here"
	photo = facebook.get('fql?q=SELECT%20pic_crop%20from%20profile%20where%20id%3D'+str(uid)).data['data'][0]['pic_crop']
	return photo['uri']

#A function that uses weighted percentages to return a semi-random match to display to our user. In its current form, we are displaying 1/8 "top matches", 1/8 close friend matches, 1/8 most upvoted matches, 1/8 most voted on matches, and 1/2 completely random matches.
def getWeightedMatch(user_obj):
	x = randint(1,16)
	if (x <= 2) and session['top_matches']:
		match_pair = (session['top_matches'][randint(0,len(session['top_matches'])-1)])
		session['top_matches'].remove(match_pair)
		user_obj.seen_top_matches.append(str((match_pair[0]['uid'],match_pair[1]['uid'])))
		user_obj.save()
	elif x == 3 and session['lifestyle_male_friends']:
		match_pair = (session['lifestyle_male_friends'][randint(0,len(session['lifestyle_male_friends'])-1)],session['female_friends'][randint(0,len(session['female_friends'])-1)])
	elif x == 4 and session['lifestyle_female_friends']:
		match_pair = (session['male_friends'][randint(0,len(session['male_friends'])-1)],session['lifestyle_female_friends'][randint(0,len(session['lifestyle_female_friends'])-1)])
	elif x >= 5 and x <= 6 and session['most_upvoted_matches']:
		match_pair = (session['most_upvoted_matches'][randint(0,len(session['most_upvoted_matches'])-1)])
		session['most_upvoted_matches'].remove(match_pair)
		if match_pair in session['most_voted_matches']:
			session['most_voted_matches'].remove(match_pair)
		user_obj.seen_top_matches.append(str((match_pair[0]['uid'],match_pair[1]['uid'])))
		user_obj.save()
	elif x >= 7 and x <= 8 and session['most_voted_matches']:
		match_pair = (session['most_voted_matches'][randint(0,len(session['most_voted_matches'])-1)])
		if match_pair in session['most_upvoted_matches']:
			session['most_upvoted_matches'].remove(match_pair)
		user_obj.seen_top_matches.append(str((match_pair[0]['uid'],match_pair[1]['uid'])))
		user_obj.save()
	else:
		match_pair = (session['male_friends'][randint(0,len(session['male_friends'])-1)],session['female_friends'][randint(0,len(session['female_friends'])-1)])
	return match_pair

#A function to query the percent upvoted for any given match.
def getPercent(match_pair):
	percentquery = Match.objects(friends__all=[str(match_pair[0]['uid']),str(match_pair[1]['uid'])]).first()
	if percentquery == None:
		acceptpercentfloat = None
	else:
		acceptpercentfloat = int(float(percentquery.num_matchers)/(percentquery.num_nonmatchers+percentquery.num_matchers) * 100)
	return acceptpercentfloat

def send_username(name):
	return requests.post(
		"https://api.mailgun.net/v2/matchboxapp.me/messages",
		auth=("api", app.config['MAILGUN_KEY']),
		data={"from": "Bill Nye <billnye@matchboxapp.me>",
			"to": ["Matchbox Team", "team@matchboxapp.me"],
			"subject": "People like you!",
			"text": name+" just signed on to Matchbox!"})

#A function to generate the amount of time that has elasped since a message was sent, to be displayed to the user.
def getTimeStamp(messagedate):
	now = datetime.datetime.now()
	timeElapsed = now - messagedate
	if timeElapsed > datetime.timedelta(days=3):
		return "%s/%s/%s at %s:%s" % (messagedate.month, messagedate.day, messagedate.year, messagedate.hour, messagedate.minute)
	elif timeElapsed > datetime.timedelta(days=1):
		return str(int(datetime.timedelta.total_seconds(timeElapsed) // 86400)) + " Days Ago"
	elif timeElapsed > datetime.timedelta(hours=1):
		return str(int(datetime.timedelta.total_seconds(timeElapsed) // 3600)) + " Hours Ago"
	elif timeElapsed > datetime.timedelta(minutes=1):
		return str(int(datetime.timedelta.total_seconds(timeElapsed) // 60)) + " Minutes Ago"
	else:
		return "Just Now"

#A function to generate random names for anonymous matches, so that users can differentiate between their chats.
def getRandomName():
	adjs = [
    "autumn", "hidden", "bitter", "misty", "silent", "empty", "dry", "dark",
    "summer", "icy", "delicate", "quiet", "white", "cool", "spring", "winter",
    "patient", "twilight", "dawn", "crimson", "wispy", "weathered", "blue",
    "billowing", "broken", "cold", "damp", "falling", "frosty", "green",
    "long", "late", "lingering", "bold", "little", "morning", "muddy", "old",
    "red", "rough", "still", "small", "sparkling", "throbbing", "shy",
    "wandering", "withered", "wild", "black", "young", "holy", "solitary",
    "fragrant", "aged", "snowy", "proud", "floral", "restless", "divine",
    "polished", "ancient", "purple", "lively", "nameless"
  	]
  	nouns = [
    "waterfall", "river", "breeze", "moon", "rain", "wind", "sea", "morning",
    "snow", "lake", "sunset", "pine", "shadow", "leaf", "dawn", "glitter",
    "forest", "hill", "cloud", "meadow", "sun", "glade", "bird", "brook",
    "butterfly", "bush", "dew", "dust", "field", "fire", "flower", "firefly",
    "feather", "grass", "haze", "mountain", "night", "pond", "darkness",
    "snowflake", "silence", "sound", "sky", "shape", "surf", "thunder",
    "violet", "water", "wildflower", "wave", "water", "resonance", "sun",
    "wood", "dream", "cherry", "tree", "fog", "frost", "voice", "paper",
    "frog", "smoke", "star"
  	]
	animals = ["adelie", "affenpinscher", "hound", "civet", "elephant", "penguin", "ainu", "akbash", "akita", "malamute", "albatross", "alligator", "dachsbracke", "bulldog","foxhound", "angelfish", "ant", "anteater", "antelope", "appenzeller", "fox", "hare", "wolf", "armadillo", "mist", "shepherd", "terrier", "avocet", "axolotl", "baboon", "camel", "badger", "balinese", "bandicoot", "barb", "barnacle", "barracuda", "basenji", "basking", "bat", "beagle", "bear", "collie", "beaver", "beetle", "bichon", "binturong", "bird", "birman", "bison", "rhinoceros", "bloodhound", "bluetick", "bobcat", "bolognese", "bombay", "bongo", "bonobo", "booby", "orangutan", "boykin", "budgerigar", "budgie", "buffalo", "bullfrog", "bumblebee", "burmese", "butterfly", "fish", "caiman", "lizard", "canaan", "capybara", "caracal", "carolina", "cassowary", "cat", "caterpillar", "catfish", "centipede", "cesky", "fousek", "chameleon", "chamois", "cheetah", "chicken", "chihuahua", "chimpanzee", "chinchilla", "chinook", "chinstrap", "chipmunk", "cichlid", "leopard", "clumber", "coati", "cockroach", "coral", "cottontop", "tamarin", "cougar", "cow", "coyote", "crab", "macaque", "crane", "crocodile", "cuscus", "cuttlefish", "dachshund", "dalmatian", "frog", "deer", "bracke", "dhole", "dingo", "discus", "doberman", "pinscher", "dodo", "dog", "dogo", "argentino", "dolphin", "donkey", "dormouse", "dragonfly", "drever", "duck", "dugong", "dunker", "dusky", "eagle", "gorilla", "echidna", "mau", "emu", "falcon", "fennec", "ferret", "flamingo", "flounder", "fly", "fossa", "frigatebird", "gar", "gecko", "gerbil", "gharial", "gibbon", "giraffe", "goat", "oriole", "retriever", "goose", "gopher", "grasshopper", "greyhound", "grouse", "guppy", "hammerhead", "shark", "hamster", "harrier", "havanese", "hedgehog", "heron", "himalayan", "hippopotamus", "horse", "humboldt", "hummingbird", "hyena", "ibis", "iguana", "impala", "indri", "insect", "setter", "wolfhound", "jackal", "jaguar", "chin", "javanese", "jellyfish", "kakapo", "kangaroo", "kingfisher", "kiwi", "koala", "kudu", "labradoodle", "ladybird", "lemming", "lemur", "liger", "lion", "lionfish", "llama", "lobster", "owl", "lynx","macaw", "magpie", "malayancivet", "maltese", "manatee", "mandrill", "markhor", "mastiff", "mayfly", "meerkat", "millipede", "mole", "molly", "mongoose", "mongrel", "monitor", "monkey", "moorhen", "moose", "eel", "moray", "moth", "mouse", "mule", "neanderthal", "neapolitan", "newfoundland", "newt", "nightingale", "numbat", "ocelot", "octopus", "okapi", "olm", "opossum", "ostrich", "otter", "oyster", "pademelon", "panther", "parrot", "peacock", "pekingese", "pelican", "persian", "pheasant", "pig", "pika", "pike", "piranha", "platypus", "pointer", "poodle", "porcupine", "possum", "prawn", "puffin", "pug", "puma", "marmoset", "pygmy","quail", "quetzal", "quokka", "quoll", "rabbit", "raccoon", "ragdoll", "rat", "rattlesnake", "reindeer", "robin", "rockhopper", "rottweiler", "salamander", "saola", "scorpion", "seahorse", "seal", "serval", "sheep", "shrimp", "siamese", "siberian", "skunk", "sloth", "snail", "snake", "snowshoe", "somali", "sparrow", "dogfish", "sponge", "squid", "squirrel", "starfish", "stickbug", "stingray", "stoat", "swan", "tang", "tapir", "tarsier", "termite", "tetra", "tiffany", "tiger", "tortoise", "toucan", "tropicbird", "tuatara", "turkey", "uakari", "uguisu", "umbrellabird", "vulture", "wallaby", "walrus", "warthog", "wasp", "weasel", "whippet", "wildebeest", "wolverine", "wombat", "woodlouse", "woodpecker", "wrasse", "yak", "yorkie", "yorkiepoo", "zebra", "zebu", "zonkey", "zorse"]
	return adjs[random.randint(0, len(adjs)-1)] + " " + animals[random.randint(0, len(animals)-1)]

class ChatNamespace(BaseNamespace):
    def initialize(self):
        self.logger = application.logger
        self.log("Socketio session started")

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def recv_connect(self):
        self.log("New connection")

    def recv_disconnect(self):
        self.log("Client disconnected")

@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    try:
        socketio_manage(request.environ, {'/chat': ChatNamespace}, request)
    except:
        application.logger.error("Exception while handling socketio connection",
                         exc_info=True)
    return Response()

