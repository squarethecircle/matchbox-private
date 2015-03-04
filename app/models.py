from mongoengine import *

class Match(Document):
	friends = ListField(StringField(max_length=30),required=True)
	friend_names = ListField(StringField(max_length=50),required=True)
	matchers = ListField(StringField(max_length=30))
	nonmatchers = ListField(StringField(max_length=30))
	confirmed = BooleanField(required=True)
