from app import db


class Match(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	friend1 = db.Column(db.String(64))
	friend2 = db.Column(db.String(64))
	matcher = db.Column(db.String(64))

