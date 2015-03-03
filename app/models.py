from mongoengine import *

class Match(Document):
	friends = ListField(StringField(max_length=30),required=True)
	matchers = ListField(StringField(max_length=30))
	nonmatchers = ListField(StringField(max_length=30))
	confirmed = BooleanField(required=True)
