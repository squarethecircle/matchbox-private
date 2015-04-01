import os
import flaskr
import unittest
import tempfile
import views.py

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

	def test_login_logout(self):
		rv = self.app.get('/login', follow_redirects=True)
		assert(rv)

	def test_session_friends(self):
		assert(session['friends'] != 0)

if __name__ == '__main__':
    unittest.main()
