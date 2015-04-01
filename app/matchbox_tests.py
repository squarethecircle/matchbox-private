import os
import unittest
import tempfile
import views

class MatchboxTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_database(self):
        test_match = Match(friends=['test1', 'test2'], friend_names=['MrTester', 'MrsTester'], matchers=[10010001000], num_matchers=1, matcher_names=['MrMatcher'], nonmatchers=[], num_nonmatchers=0, nonmatcher_names=[], confirmed=false)
        add_database = test_match.save()

        get_database = Match.objects(friends__all=['test1', 'test2']).first()
        assert(add_database == get_database)

	def test_session(self):
		assert(session['male_friends'])
        assert(session['female_friends'])

    def test_facebook_query(self):
        assert(session.get('facebook_token'))
        session.get('me')

if __name__ == '__main__':
    unittest.main()
