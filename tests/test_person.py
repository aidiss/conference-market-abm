import unittest
from conference_market.agents import Person
from conference_market.model import ConferenceModel, Conference

from conference_market.agents import JobPostingSite
from conference_market.agents import Facebook

import datetime


class TestPersonAssessConference(unittest.TestCase):
    """Person is assessing the value of the event"""

    def setUp(self):
        model = ConferenceModel()
        self.person = Person(1, model)
        self.person.interests = "a lof of great technologies"
        self.conference = Conference.from_faker_conference(2, model)
        self.conference.description = "very interesting conference about python"

    @unittest.SkipTest
    def test_person_assess_conference(self):
        match = self.person.assess_conference_topic(self.conference)
        self.assertEqual(match, 100)


class TestPersonBuyConferenceTicket(unittest.TestCase):
    """Person tries to buy a ticket to a conference"""

    def setUp(self):
        self.model = ConferenceModel()
        self.person = Person(1, self.model)
        self.conference = Conference.from_faker_conference(13, self.model)

    def test_person_buy_ticket_succesfull_purchase(self):
        self.person.buy_conference_ticket(self.conference)
        print(self.person.wealth)
        print(self.conference)
        self.assertIsNotNone(self.person.tickets)


class TestPersonBrowseJobAdds(unittest.TestCase):
    """Person tries browse job adds"""

    def setUp(self):
        model = ConferenceModel()
        self.person = Person(1, model)
        self.job_posting_site = JobPostingSite(1, model)

    def test_person_browse_job_adds(self):
        self.person.browse_job_postings(self.job_posting_site)


class TestPersonBrowseFacebook(unittest.TestCase):
    """Person browses facebook"""

    def setUp(self):
        model = ConferenceModel()
        conference = Conference.from_faker_conference(1, model)
        model.facebook.create_event(
            "test_event_name", 'test_host_name', conference)
        self.person = Person(1, model)

    def test_person_browse_facebook(self):
        self.person.browse_facebook()
        event = self.person.events_seen[0]
        self.assertEqual('test_event_name', event.name)
        self.assertEqual('test_host_name', event.host)


class TestAssessSeenFacebookEvents(unittest.TestCase):
    """Person browses facebook"""

    def setUp(self):
        model = ConferenceModel()
        conference = Conference.from_faker_conference(1, model)
        model.facebook.create_event(
            "test_event_name", 'test_host_name', conference)
        self.person = Person(1, model)

    def test_person_browse_facebook(self):
        self.person.browse_facebook()
        self.person.assess_seen_events()
        self.assertEqual(len(self.person.tickets), 1)
