from flask import Response,request
from app import app,models
from models import User
from socketio import socketio_manage
from socketio.mixins import RoomsMixin
from socketio.namespace import BaseNamespace
from chat import newMessage

class ChatNamespace(BaseNamespace,RoomsMixin):
	def initialize(self):
		self.room="NULL"
		self.logger = app.logger
		self.log("Socketio session started")

	def log(self, message):
		self.logger.info("[{0}] [{2}] {1}".format(self.socket.sessid, message,self.room))

	def recv_connect(self):
		self.log("New connection")

	def on_join(self,token):
		self.log('got token: %s' % token)
		user=User.objects(chat_token=token).first()
		self.room=user.fbid
		self.join(user.fbid)
		return True

	def recv_disconnect(self):
		self.log("Client disconnected")

	def emit_to_room(self, room, event, *args):
		"""This is sent to all in the room (in this particular Namespace)"""
		pkt = dict(type="event",
				   name=event,
				   args=args,
				   endpoint=self.ns_name)
		room_name = self._get_room_name(room)
		for sessid, socket in self.socket.server.sockets.iteritems():
			if 'rooms' not in socket.session:
				continue
			if room_name in socket.session['rooms']:
				socket.send_packet(pkt)

	def on_message(self, message):
		self.log('got a message: %s' % message)
		newMessage(self.room,message['recipient'],message['text'])
		self.emit_to_room(self.room,'message',message['recipient'],message['text'],0)
		self.emit_to_room(message['recipient'],'message',self.room,message['text'],1)
		return True, message
@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
	try:
		socketio_manage(request.environ, {'/chat': ChatNamespace}, request)
	except:
		app.logger.error("Exception while handling socketio connection",
						 exc_info=True)
	return Response()

