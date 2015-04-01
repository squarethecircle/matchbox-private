import os
import unittest
import tempfile
from app import app, views, models

# Test data to allow us to set the session variables
lifestyle_male_friends = []
lifestyle_female_friends = []
lifestyle_ids = [100000117930891, 1673808394, 749512978, 629263828, 1120293045, 100000279378280, 1646941022, 644659874, 707859779, 774168034, 821596896, 1235948517, 1306399238, 1293191998, 1391794445, 1471153226, 1522524524, 1666913902, 1577529446, 1598222289, 100004191697613, 100000359149448, 100000892201552, 100001288758840]
top_matches_ids = [(1375642201, 1646941022), (705579939, 100003888319326), (644659874, 1425476801), (707859779, 1321417892), (707859779, 100005920514441), (644659874, 100005920514441), (1375642201, 1522524524), (1306399238, 100000742350322), (1293191998, 100000742350322), (1235948517, 100004191697613), (100000279378280, 1397434942),  (100000486251970, 1490615349),  (100004797271381, 100000163821701), (100000117930891, 1391794445), (100000117930891, 1471153226), (821596896, 1471153226), (774168034,  1397434942), (100000117930891, 1321417892), (100000279378280, 1490615349), (821596896, 1391794445), (774168034, 100001663293430), (100000279378280, 1321417892), (774168034, 100000742350322), (1293191998, 1321417892), (1293191998, 1471153226), (100000279378280, 100000163821701), (1293191998, 1391794445), (100004797271381, 1425476801), (100000892201552, 1425476801), (100000892201552, 1522524524), (100000279378280, 1248783721), (100002804284636, 1248783721)]
male_friends = [{
      "name": "Mr Test 1", 
      "relationship_status": "", 
      "sex": "male", 
      "uid": 6514
    }, 
    {
      "name": "Mr Test 2", 
      "relationship_status": "In a relationship", 
      "sex": "male", 
      "uid": 502602860
    }, 
    {
      "name": "Mr Test 3", 
      "relationship_status": "", 
      "sex": "male", 
      "uid": 503939168
    }]
female_friends = [{
      "name": "Mrs Test 1", 
      "relationship_status": "", 
      "sex": "female", 
      "uid": 65141
    }, 
    {
      "name": "Mrs Test 2", 
      "relationship_status": "In a relationship", 
      "sex": "female", 
      "uid": 5026028601
    }, 
    {
      "name": "Mrs Test 3", 
      "relationship_status": "", 
      "sex": "female", 
      "uid": 5039391681
    }]
top_matches = []
most_upvoted_matches = []
most_voted_matches = []
fbid = '1234'
name = 'Testing'


class MatchboxTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        with self.app as c:
            with c.session_transaction() as session:
                session['fbid'] = fbid
                session['name'] = name
                session['male_friends'] = male_friends
                session['female_friends'] = female_friends
                session['lifestyle_male_friends'] = lifestyle_male_friends
                session['lifestyle_female_friends'] = lifestyle_female_friends
                session['top_matches'] = top_matches
                session['most_upvoted_matches'] = most_upvoted_matches
                session['most_voted_matches'] = most_voted_matches

        query = models.User.objects(fbid=session['fbid']).first()
        if query == None:
            new_user = models.User(fbid=session['fbid'],name=session['name'],seen_top_matches=[],num_submitted=0)
            new_user.save() 

    def test_database(self):
        test_match = models.Match(friends=['100100', '100101'], friend_names=['MrTester', 'MrsTester'], matchers=['10010001000'], num_matchers=1, matcher_names=['MrMatcher'], nonmatchers=[], num_nonmatchers=0, nonmatcher_names=[], confirmed=False)
        add_database = test_match.save()

        get_database = models.Match.objects(friends__all=['100100', '100101']).first()
        assert(add_database.friends == get_database.friends)

    def test_add_accept_match(self):
        self.app.post('match', data={'friend1':'100100', 'friend2':'100101', 
            'friend1name':'MrTester', 'friend2name':'MrsTester', 'result':'accept'})
        
        # print models.Match.objects()
        # print models.Match.objects()[0].friends

        get_database = models.Match.objects(friends__all=['100100','100101']).first()
        assert(get_database.num_matchers==1)

    def test_add_reject_match(self):
        self.app.post('match', data={'friend1':'100100', 'friend2':'100101', 
            'friend1name':'MrTester', 'friend2name':'MrsTester', 'result':'reject'})
        
        # print models.Match.objects()
        # print models.Match.objects()[0].friends

        get_database = models.Match.objects(friends__all=['100100','100101']).first()
        assert(get_database.num_nonmatchers==1)

    def test_increment_match(self):
        test_match = models.Match(friends=['200100', '200101'], friend_names=['MrTester', 'MrsTester'], matchers=['10010001000'], num_matchers=1, matcher_names=['MrMatcher'], nonmatchers=[], num_nonmatchers=0, nonmatcher_names=[], confirmed=False)
        test_match.save()
        
        # print models.Match.objects().all()
        # print models.Match.objects()[0].friends

        self.app.post('match', data={'friend1':'200100', 'friend2':'200101', 
            'friend1name':'MrTester', 'friend2name':'MrsTester', 'result':'accept'})

        get_database = models.Match.objects(friends__all=['200100', '200101']).first()
        assert(get_database.num_matchers==2)

    # def test_percent(self):
    #     match_pair = views.getWeightedMatch(query)
    #     acceptpercentfloat = views.getPercent(match_pair)

    #     if acceptpercentfloat == None:
    #         acceptpercent = "No Data"
    #         rejectpercent = "No Data"
    #     else:
    #         acceptpercent = str(acceptpercentfloat) + "%"
    #         rejectpercent = str(100-acceptpercentfloat) + "%"

    #     assert(acceptpercent)
    #     assert(rejectpercent)


    # def tearDown(self):
    #     os.unlink(app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()
