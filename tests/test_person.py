import unittest
from conference_market.agents import Person
from conference_market.model import ConferenceModel, Conference

from conference_market.agents import JobPostingSite
import datetime


class TestPersonAssessConference(unittest.TestCase):
    """Person is assessing the value of the event"""

    def setUp(self):
        model = ConferenceModel()
        self.person = Person(1, model)
        self.person.interests = "a lof of great technologies"
        self.conference = Conference.from_faker_conference(2, model)
        self.conference.description = "very interesting conference about python"

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
