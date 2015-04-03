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
	name = StringField(max_length=100)
	seen_top_matches = ListField(StringField(max_length=80))
	num_submitted = IntField(required=True)
	chat_token = StringField(max_length=64)

class Message(EmbeddedDocument):
	sender = StringField(max_length=30)
	recipient = StringField(max_length=30)
	text = StringField()
	sent_time = DateTimeField()

class RevealChoice(EmbeddedDocument):
	user = StringField(max_length=30,required=True)
	fake_user = StringField(required=True)
	status = BooleanField(default=False)


class Chat(Document):
	pair = ListField(StringField(max_length=30))
	reveals = ListField(EmbeddedDocumentField(RevealChoice))
	messages = SortedListField(EmbeddedDocumentField(Message),ordering='sent_time',reverse=True)