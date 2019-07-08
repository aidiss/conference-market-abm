import unittest
from conference_market.agents import Facebook
from conference_market.model import ConferenceModel, Conference

import datetime
from facebook import FacebookEvent
from conference_market.agents import Person


class TestFacebookCreateEvent(unittest.TestCase):
    """Create an event

    Event should have:

    name
    Start date
    End date
    Description
    Created by (page, or group)
    """

    def setUp(self):
        model = ConferenceModel()
        self.facebook = Facebook(1, model)
        self.person = Person(2, model)

    def test_facebook_create_event(self):
        self.facebook.create_event(name="PyConLT 2020", host=self)
        created_event = self.facebook.events[0]
        self.assertIsInstance(created_event, FacebookEvent)
        self.assertEqual(created_event.name, "PyConLT 2020")


class TestFacebookAdvertisment(unittest.TestCase):
    """Advertisment"""

    def setUp(self):
        model = ConferenceModel()
        self.facebook = Facebook(1, model)

    def test_facebook_create_event(self):
        self.facebook.create_event_advertisment
