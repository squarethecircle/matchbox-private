from mongoengine import *

class Match(Document):
	friends = ListField(StringField(max_length=30),required=True)
	friend_names = ListField(StringField(max_length=50),required=True)
	matchers = ListField(StringField(max_length=30))
	matcher_names = ListField(StringField(max_length=100))
	num_matchers = IntField(required=True)
	nonmatchers = ListField(StringField(max_length=30))
	num_nonmatchers = IntField(required=True)
	nonmatcher_names = ListField(StringField(max_length=100))
	confirmed = BooleanField(required=True)

class User(Document):
	fbid = StringField(max_length=30,unique=True)
	seen_top_matches = ListField(StringField(max_length=80))
	num_submitted = IntField(required=True)
