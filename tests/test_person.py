import unittest
from conference_market.agents import Person
from conference_market.model import ConferenceModel, Conference

import datetime


class TestAgentAssessConference(unittest.TestCase):
    """Person is assessing the value of the event"""

    def setUp(self):
        self.model = ConferenceModel()
        self.model.date = datetime.datetime.now()
        self.person = Person(1, self.model)
        self.conference = Conference.from_faker_conference(13, self.model)

    def test_assess_conference(self):
        self.person.check_for_conferences()
        self.person.consider_buying_a_ticket(self.conference, 2, 2)
        self.assertAlmostEqual


class TestPersonBuyConferenceTicket(unittest.TestCase):
    """Person tries to buy a ticket to a conference"""

    def setUp(self):
        self.model = ConferenceModel()
        self.model.date = datetime.datetime.now()
        self.person = Person(1, self.model)
        self.conference = Conference.from_faker_conference(13, self.model)

    def test_succesfull_purchase(self):
        self.person.buy_conference_ticket(self.conference)
        print(self.person.wealth)
        print(self.conference)
        self.assertIsNotNone(self.person.tickets)


if __name__ == '__main__':
    unittest.main()
