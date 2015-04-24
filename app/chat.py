from flask import render_template,session,redirect,url_for,request,jsonify,Response
from binascii import hexlify
from os import urandom
from app import app,models,facebook
from models import User, Chat, Message,RevealChoice
import datetime
from random import randint
import requests

@app.route('/chat')
def chat():
	if session.get('facebook_token') is None:
		return redirect('/login?next=%2Fchat')
	if request.args.get('token') == 'false':
		token=User.objects(fbid=session['fbid']).first().chat_token
	#else:
	token=hexlify(urandom(32))
	user=User.objects(fbid=session['fbid']).update_one(set__chat_token=token)
	query=Chat.objects(pair__all=[session['fbid']]).order_by('-messages')
	#chats_filtered=[]
	#for chat in chats:
	#	if chat.reveals[0].status is False or chat.reveals[1].status is False
	chats=[]
	for chat in query:
		chat.pair.remove(session['fbid'])
		other=chat.pair[0]
		if chat.reveals[0].user == session['fbid']:
			my_reveals=chat.reveals[0]
			other_reveals=chat.reveals[1]
		else:
			my_reveals=chat.reveals[1]
			other_reveals=chat.reveals[0]
		if my_reveals.status and other_reveals.status:
			name=requests.get('http://graph.facebook.com/'+other).json()['name']
			photo=requests.get('http://graph.facebook.com/'+other+'/picture?width=40&height=40',allow_redirects=False).headers['location']
		else:
			name = other_reveals.fake_user
			if requests.get('http://graph.facebook.com/'+other).json()['gender'] == "male":
				photo="static/img/male1.jpg"
			else:
				photo="static/img/female.jpg"
		desc = ""
		if len(chat.messages) > 0:
			desc = chat.messages[-1].text
		chats.append({'name':name,'fbid':other,'photo':photo,'desc':desc,'status':my_reveals.status})
	#return jsonify({'data':query[0].messages})
	if query:
		messages=query[0].messages
	else:
		messages=[]
	other_string=""
	current_user=chats[0]['fbid']
	if request.args.get('current'):
		current_user=request.args.get('current')
	if chats:
		other_string='data-user=%s' % current_user
	return render_template('chat.html',token=token,my_fbid=session['fbid'],chats=chats,other_fbid=other_string,
		messages=messages,view_func=getTimeStamp,twenty_minutes=datetime.timedelta(minutes=20))

@app.route('/getChat')
def getChat():
	query=Chat.objects(pair__all=[session['fbid'],request.args.get('fbid')]).first()
	if query:
		messages=query.messages
	else:
		messages=[]
	other_string='data-user=%s' % request.args.get('fbid')
	return render_template('chat_partial.html',my_fbid=session['fbid'],other_fbid=other_string,messages=messages,
		view_func=getTimeStamp,twenty_minutes=datetime.timedelta(minutes=20))

def newMessage(sender,receiver,msg):
	new_msg = Message(sender=sender,recipient=receiver,text=msg,sent_time=datetime.datetime.now())
	chat = Chat.objects(pair__all=[sender,receiver]).first()
	if chat is None:
		createChat(sender,receiver)
	chat.update(add_to_set__messages=[new_msg])

def createChat(user1,user2,anonymous=True):
	#name1=User.objects(fbid=user1).first().name
	#name2=User.objects(fbid=user2).first().name
	if anonymous:
		reveal1 = RevealChoice(user=user1,fake_user=getRandomName().title())
		reveal2 = RevealChoice(user=user2,fake_user=getRandomName().title())
	else:
		reveal1 = RevealChoice(user=user1,fake_user=getRandomName().title(),status=True)
		reveal2 = RevealChoice(user=user2,fake_user=getRandomName().title(),status=True)
	new_chat = Chat(pair=[user1,user2],reveals=[reveal1,reveal2])
	new_chat.save()

@app.route('/reveal',methods=['POST'])
def changeStatus():
	other_id = request.form.get('other')
	my_id = session['fbid']
	status = request.form.get('status')
	chat=Chat.objects(pair__all=[my_id,other_id]).first()
	if chat.reveals[0].user == session['fbid']:
		my_reveals=chat.reveals[0]
		other_reveals=chat.reveals[1]
	else:
		my_reveals=chat.reveals[1]
		other_reveals=chat.reveals[0]
	if status == "1":
		my_reveals.status=True
		chat.save()
	elif status == "0":
		my_reveals.status=False
		chat.save()
	return "Success"

@app.route('/jsonifyChat')
def jsonifyChat():
	if session.get('facebook_token') is None:
		return redirect('/login?next=%2Fchat')
	if request.args.get('token') == 'false':
		token=User.objects(fbid=session['fbid']).first().chat_token
	#else:
	token=hexlify(urandom(32))
	user=User.objects(fbid=session['fbid']).update_one(set__chat_token=token)
	query=Chat.objects(pair__all=[session['fbid']]).order_by('-messages')
	#chats_filtered=[]
	#for chat in chats:
	#	if chat.reveals[0].status is False or chat.reveals[1].status is False
	chats=[]
	for chat in query:
		chat.pair.remove(session['fbid'])
		other=chat.pair[0]
		if chat.reveals[0].user == session['fbid']:
			my_reveals=chat.reveals[0]
			other_reveals=chat.reveals[1]
		else:
			my_reveals=chat.reveals[1]
			other_reveals=chat.reveals[0]
		if my_reveals.status and other_reveals.status:
			name=requests.get('http://graph.facebook.com/'+other).json()['name']
			photo=requests.get('http://graph.facebook.com/'+other+'/picture?width=40&height=40',allow_redirects=False).headers['location']
		else:
			name = other_reveals.fake_user
			if requests.get('http://graph.facebook.com/'+other).json()['gender'] == "male":
				photo="static/img/male1.jpg"
			else:
				photo="static/img/female.jpg"
		desc = ""
		if len(chat.messages) > 0:
			desc = chat.messages[-1].text
		chats.append({'name':name,'fbid':other,'photo':photo,'desc':desc,'status':my_reveals.status})
	#return jsonify({'data':query[0].messages})
	if query:
		messages=query[0].messages
	else:
		messages=[]
	other_string=""
	current_user=chats[0]['fbid']
	if request.args.get('current'):
		current_user=request.args.get('current')
	if chats:
		other_string='data-user=%s' % current_user
	json_messages = []
	for message in messages:
		json_message = {'sender':message.sender,'recipient':message.recipient,'text':message.text}
		json_messages.append(json_message)
	ChatJSon = {'token':token, 'my_fbid':session['fbid'], 'chats':chats, 'other_fbid':other_string, 'messages':json_messages}
	return jsonify(ChatJSon)

@app.route('/retrieveMessages')
def getMessages():
	user = session['fbid']
	other = request.args.get('other')
	messages = Chat.objects(pair__all=[user,other]).first().messages
	json_messages = []
	for message in messages:
		json_message = {'sender':message.sender,'recipient':message.recipient,'text':message.text,
		'sent_time':message.sent_time.strftime('%m/%d/%Y %I:%M:%S %p')}
		json_messages.append(json_message)
	return jsonify({"messages":json_messages})

# A function to generate random names for anonymous matches, so that users can differentiate between their chats.
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
	animals = ["adelie", "affenpinscher", "hound", "civet", "elephant", "penguin", "ainu", "akbash", "akita", 
	"malamute", "albatross", "alligator", "dachsbracke", "bulldog","foxhound", "angelfish", "ant", "anteater", 
	"antelope", "appenzeller", "fox", "hare", "wolf", "armadillo", "mist", "shepherd", "terrier", "avocet", 
	"axolotl", "baboon", "camel", "badger", "balinese", "bandicoot", "barb", "barnacle", "barracuda", "basenji", 
	"basking", "bat", "beagle", "bear", "collie", "beaver", "beetle", "bichon", "binturong", "bird", "birman", "bison", 
	"rhinoceros", "bloodhound", "bluetick", "bobcat", "bolognese", "bombay", "bongo", "bonobo", "booby", "orangutan", 
	"boykin", "budgerigar", "budgie", "buffalo", "bullfrog", "bumblebee", "burmese", "butterfly", "fish", "caiman", "lizard", 
	"canaan", "capybara", "caracal", "carolina", "cassowary", "cat", "caterpillar", "catfish", "centipede", "cesky", "fousek", 
	"chameleon", "chamois", "cheetah", "chicken", "chihuahua", "chimpanzee", "chinchilla", "chinook", "chinstrap", "chipmunk", 
	"cichlid", "leopard", "clumber", "coati", "cockroach", "coral", "cottontop", "tamarin", "cougar", "cow", "coyote", "crab", 
	"macaque", "crane", "crocodile", "cuscus", "cuttlefish", "dachshund", "dalmatian", "frog", "deer", "bracke", "dhole", 
	"dingo", "discus", "doberman", "pinscher", "dodo", "dog", "dogo", "argentino", "dolphin", "donkey", "dormouse", "dragonfly", 
	"drever", "duck", "dugong", "dunker", "dusky", "eagle", "gorilla", "echidna", "mau", "emu", "falcon", "fennec", "ferret", 
	"flamingo", "flounder", "fly", "fossa", "frigatebird", "gar", "gecko", "gerbil", "gharial", "gibbon", "giraffe", "goat", 
	"oriole", "retriever", "goose", "gopher", "grasshopper", "greyhound", "grouse", "guppy", "hammerhead", "shark", "hamster", 
	"harrier", "havanese", "hedgehog", "heron", "himalayan", "hippopotamus", "horse", "humboldt", "hummingbird", "hyena", "ibis", 
	"iguana", "impala", "indri", "insect", "setter", "wolfhound", "jackal", "jaguar", "chin", "javanese", "jellyfish", "kakapo", 
	"kangaroo", "kingfisher", "kiwi", "koala", "kudu", "labradoodle", "ladybird", "lemming", "lemur", "liger", "lion", "lionfish", 
	"llama", "lobster", "owl", "lynx","macaw", "magpie", "malayancivet", "maltese", "manatee", "mandrill", "markhor", "mastiff", 
	"mayfly", "meerkat", "millipede", "mole", "molly", "mongoose", "mongrel", "monitor", "monkey", "moorhen", "moose", "eel", 
	"moray", "moth", "mouse", "mule", "neanderthal", "neapolitan", "newfoundland", "newt", "nightingale", "numbat", "ocelot", 
	"octopus", "okapi", "olm", "opossum", "ostrich", "otter", "oyster", "pademelon", "panther", "parrot", "peacock", "pekingese", 
	"pelican", "persian", "pheasant", "pig", "pika", "pike", "piranha", "platypus", "pointer", "poodle", "porcupine", "possum", 
	"prawn", "puffin", "pug", "puma", "marmoset", "pygmy","quail", "quetzal", "quokka", "quoll", "rabbit", "raccoon", "ragdoll", 
	"rat", "rattlesnake", "reindeer", "robin", "rockhopper", "rottweiler", "salamander", "saola", "scorpion", "seahorse", "seal", 
	"serval", "sheep", "shrimp", "siamese", "siberian", "skunk", "sloth", "snail", "snake", "snowshoe", "somali", "sparrow", "dogfish",
	 "sponge", "squid", "squirrel", "starfish", "stickbug", "stingray", "stoat", "swan", "tang", "tapir", "tarsier", "termite", "tetra",
	  "tiffany", "tiger", "tortoise", "toucan", "tropicbird", "tuatara", "turkey", "uakari", "uguisu", "umbrellabird", "vulture", 
	  "wallaby", "walrus", "warthog", "wasp", "weasel", "whippet", "wildebeest", "wolverine", "wombat", "woodlouse", "woodpecker", 
	  "wrasse", "yak", "yorkie", "yorkiepoo", "zebra", "zebu", "zonkey", "zorse"]
	return adjs[randint(0, len(adjs)-1)] + " " + animals[randint(0, len(animals)-1)]
# A function to generate the amount of time that has elasped since a message was sent, to be displayed to the user.
def getTimeStamp(value):
	"""
	Finds the difference between the datetime value given and now()
	and returns appropriate humanize form
	"""
	from datetime import datetime
 
	if isinstance(value, datetime):
		delta = datetime.now() - value
		if delta.days > 6:
			return value.strftime("%b %d")                    # May 15
		if delta.days > 1:
			return value.strftime("%A")                       # Wednesday
		elif delta.days == 1:
			return 'yesterday'                                # yesterday
		elif delta.seconds > 7200:
			return str(delta.seconds / 3600 ) + ' hours ago'  # 3 hours ago
		elif delta.seconds > 3600:
			 return str(delta.seconds / 3600 ) + ' hour ago'  # 3 hours ago
		elif delta.seconds >  120:
			return str(delta.seconds/60) + ' minutes ago'     # 29 minutes ago
		else:
			return 'a moment ago'                             # a moment ago





