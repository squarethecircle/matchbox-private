import os
import unittest
import tempfile
from app import app, views, models

class MatchboxTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        with self.app as c:
            with c.session_transaction() as sess:
                sess['fbid'] = '12345'

    def test_database(self):
        test_match = models.Match(friends=['100100', '100100'], friend_names=['MrTester', 'MrsTester'], matchers=['10010001000'], num_matchers=1, matcher_names=['MrMatcher'], nonmatchers=[], num_nonmatchers=0, nonmatcher_names=[], confirmed=false)
        add_database = test_match.save()

        get_database = models.Match.objects(friends__all=['test1', 'test2']).first()
        assert(add_database == get_database)

    def test_add_match(self):
        self.app.post('match', {friend1:'100100', friend2:'100100', 
            friend1name:'MrTester', friend2name:'MrsTester', result:'accept'})

        get_database = models.Match.objects(friends__all=['100100','100100']).first()
        assert(get_database)

    def test_increment_match(self):
        test_match = models.Match(friends=['100100', '100100'], friend_names=['MrTester', 'MrsTester'], matchers=['10010001000'], num_matchers=1, matcher_names=['MrMatcher'], nonmatchers=[], num_nonmatchers=0, nonmatcher_names=[], confirmed=false)
        add_database = test_match.save()

        self.app.post('match', {friend1:'100100', friend2:'100100', 
            friend1name:'MrTester', friend2name:'MrsTester', result:'accept'})

        get_database = models.Match.object(friends__all=['100100', '100100']).first()
        assert(get_database.num_matchers==2)

    # def tearDown(self):
    #     os.unlink(app.config['DATABASE'])

    # def test_session(self):
    #     assert(session['male_friends'])
    #     assert(session['female_friends'])

    # def test_facebook_query(self):
    #     assert(session.get('facebook_token'))
    #     session.get('me')

if __name__ == '__main__':
    unittest.main()
