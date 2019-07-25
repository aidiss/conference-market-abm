from datetime import datetime
from random import choice, randint, random
from typing import List

import numpy as np

from fuzzywuzzy.fuzz import partial_token_set_ratio, ratio, token_set_ratio
from mesa import Agent, Model
from conference_market.models import JobPosting, FacebookEventAdvertisment, Ticket
from conference_market.utils import load_stackshare_techs, load_techs, load_stackoverflow_tags
from facebook import FacebookEvent

from conference_market.faker_provider import fake
import logging

REPORTING = False


techs = load_techs()
techs = load_stackshare_techs()
techs = load_stackoverflow_tags()
interest_modes = [partial_token_set_ratio, token_set_ratio, ratio]


class JobPostingSite:
    """Job posting site"""

    def __init__(self, unique_id: int, model: Model):
        self.unique_id = unique_id
        self.model = model
        self.job_postings = []

    def publish_job_posting(self, name, description, company):
        job_posting = JobPosting(name, description, company)
        self.job_postings.append(job_posting)

    def publish_new_postings(self):
        pass

    def remove_canceled_postings(self):
        pass

    def remove_expired_postings(self):
        self.postings = [p for p in self.job_postings if not p.expired]
        pass

    def step(self):
        # Review postings and publis them
        self.publish_new_postings()
        # Look through all postings and remove ones that are canceled
        self.remove_canceled_postings()
        # Remove expired
        self.remove_expired_postings()


class Conference:
    """A conference is a gathering of individuals
    who meet at an arranged place and time
    in order to discuss or engage in some common interest.
    """

    def __init__(
        self,
        unique_id: int,
        model: Model,
        name: str,
        start_date: datetime,  # When it starts, important for participants
        end_date: datetime,  # Not really important
        price: str,  # Price, how much person should pay to enter the event. Simplified
        visibility: float,  # Generic visibility. Todo: Make visibility less abstract
        topics: List[str],  # Each topic is a string
        wealth: int,  # A budget of the event. Maybe its budget of company that organizes it
        city: str,  # important, as travel to other place ia anuisance
    ):
        self.unique_id: int = unique_id
        self.model = model
        self.name: str = name
        self.start_date: datetime = start_date
        self.end_date: datetime = end_date
        self.price: float = price
        self.visibility: float = visibility or 0.1
        self.topics: str = [topic.lower().replace(' ', '-')
                            for topic in topics]
        self.wealth: float = wealth or 500
        self.ticket_sold_count = 0
        self.city = city
        self.tickets: List[Ticket] = []

        self.event_posted = False
        print(self.topics)

    @classmethod
    def from_faker_conference(cls, unique_id, model, **kwargs):
        """Generates a conference from fake data"""
        return cls(unique_id, model, **fake.conference())

    def __repr__(self):
        return str(self.__class__.__name__) + str(self.__dict__)

    def select_date(self):
        if self.start_date:
            return
        # Select date if no date is setself.

    def publish_cfp(self):
        if not self.start_date:
            return

        # Check what is the preference?
        pass

    def publish_event(self):
        """Publish event. I guess on website"""
        self.model.facebook.create_event('name', 'host', conference=self)

    def step(self):
        """Steps are made day"""

        # Advertise
        self.select_date()
        self.publish_cfp()
        if not self.event_posted:
            self.publish_event()

        if REPORTING:
            self.dump_report()

    def dump_report(self):
        self.model.datacollector.add_table_row(
            table_name="conferences",
            row={
                "unique_id": self.unique_id,
                "name": self.name,
                "ticket_sold_count": self.ticket_sold_count,
                "date": self.model.date,
            },
        )


class Person(Agent):
    def __init__(self, unique_id: int, model: Model, *args, **kwargs):
        super().__init__(unique_id, model)
        self.wealth = 500
        self.monthly_income = randint(300, 1500)
        self.daily_food_expenses = randint(5, 10)
        self.monthly_taxes = randint(100, 500)
        self.tickets = []
        interest_width = randint(1, 10)
        self.interests = [choice(techs) for x in range(interest_width)]
        self.interest_matching_mode = choice(interest_modes)
        self.is_employed = True
        self.awareness = np.random.normal(0.5, 0.2)
        self.city = choice(
            ["kaunas", "vilnius", "vilnius", "vilnius", "vilnius"])
        self.events_seen = []

    @classmethod
    def from_faker_profile(cls, unique_id, model, **kwargs):
        """Generates a person from faker profile"""

        return cls(unique_id, model)
        # return cls(unique_id, model, **fake.profile())

    def assess_seen_events(self):
        """Go through seen events"""
        random_choice = choice(self.events_seen).conference
        days_till_event = random_choice.start_date - self.model.date
        # Will not be buying a ticket to event which is already over.
        if days_till_event.days <= 0:
            return

        buy_chance = 1 / (days_till_event.days ** 1.5)

        if random_choice.city != self.city:
            buy_chance /= 5

        if buy_chance >= .2:
            # buy_chance *= (buy_chance / 1) + 1
            buy_chance = .2

        if random() < buy_chance:
            self.buy_conference_ticket(random_choice)

    def attend_event(self):
        """Attend event

        Knowledge and relationships should change"""

        self.tickets = []

    def buy_conference_ticket(self, conference):
        """Buy a conference ticket buy transfering money"""
        log_msg = "Person with interests %s is buying a ticket to %s"
        logging.debug(log_msg, ','.join(self.interests), conference.name)
        self.wealth -= conference.price
        conference.wealth += conference.price
        self.tickets.append(conference)
        conference.ticket_sold_count += 1
        if REPORTING:
            self._report_purchase(conference)

    def browse_facebook(self):
        """Browse facebook"""
        for event in self.model.facebook.events:
            self.events_seen.append(event)

    def step(self):
        """Steps done in a day.

        A person does a lot of stuff in a daily routine. He or she wakes up, showers, eats breakfast,
        commutes to work"""

        # You need to check facebook
        if not self.tickets:
            self.browse_facebook()

        # You need to check facebook
        if not self.tickets and self.events_seen:
            self.assess_seen_events()

        # you have a ticket, why not attending?
        if self.tickets:
            if self.model.date in [t.start_date for t in self.tickets]:
                self.attend_event()

    def _report_interest(self, interest):
        self.model.datacollector.add_table_row(
            table_name='interest',
            row={
                'unique_id': self.unique_id,
                'interest': interest,
                'date': self.model.date
            }
        )

    def _report_purchase(self, conference):
        self.model.datacollector.add_table_row(
            table_name="purchase",
            row={
                "unique_id": self.unique_id,
                "conference_name": conference.name,
                "wealth": self.wealth,
                "date": self.model.date,
            },
        )

    def __repr__(self):
        return str(self.__class__.__name__) + str(self.__dict__)


class Facebook:
    """Facebook"""

    def __init__(self, unique_id: int, model: Model):
        self.unique_id = unique_id
        self.model = model
        self.events: List[FacebookEvent] = []
        self.posts = []
        self.advertisments = []
        # typing:
        self.event_advertisments: List[FacebookEventAdvertisment] = []

    def create_event(self, name, host, conference):
        """Create an event that can be like and participated by Facebook Users

        Consider: done by user?"""
        facebook_event = FacebookEvent(
            name=name, host=host, conference=conference)
        self.events.append(facebook_event)

    def create_event_advertisment(self, event, payer, budget):
        """Create advertisment that will be showed to anyeone who will be vising facebook"""
        facebook_event_advertisment = FacebookEventAdvertisment(
            event, payer, budget)
        self.event_advertisments.append(facebook_event_advertisment)

    def advertise(self):
        for add in self.event_advertisments:
            add

    def charge_for_advertisments(self):
        if self.model.date.day != 10:
            return

        for add in self.event_advertisments:
            add

    def step(self):
        self.advertise()
        self.charge_for_advertisments()
