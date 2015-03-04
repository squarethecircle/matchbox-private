#!flask/bin/python
from app import app
import os
if os.environ['MATCHMAKING_STATUS'] == 'DEBUG':
	app.run(debug=True)
else:
	app.run()


