from datetime import datetime
from random import choice, randint, random
from typing import List

import numpy as np
from faker import Faker
from faker.providers import BaseProvider
from fuzzywuzzy.fuzz import partial_token_set_ratio, ratio, token_set_ratio
from mesa import Agent, Model

from conference_market.utils import load_stackshare_techs, load_techs

techs = load_techs()
techs = load_stackshare_techs()
interest_modes = [partial_token_set_ratio, token_set_ratio, ratio]

fake = Faker()


class ConferenceProvider(BaseProvider):
    conferences = ["one", "two", "three"]

    def conference(self):
        return dict(
            name=self.random_element(self.conferences),
            wealth=self.wealth(),
            start_date=self.start_date(),
            end_date=self.start_date(),
            price=self.price(),
            visibility=self.visibility(),
            topics=[self.topic() for _ in range(10)],
        )

    def wealth(self):
        return self.random_digit()

    def start_date(self):
        return fake.date()

    def end_date(self):
        return fake.date()

    def price(self):
        return fake.date()

    def visibility(self):
        return self.random_int()

    def topic(self):
        return "asd"


fake.add_provider(ConferenceProvider)


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
        self.city = choice(["kaunas", "vilnius", "vilnius"])

    @classmethod
    def from_faker_profile(cls, unique_id, model):
        """Generates a person from faker profile"""
        return cls(unique_id, model, **fake.profile())

    def assess_conference(self, conference):
        # Did person see the conference
        if conference.visibility < self.awareness:
            return

        # Do not consider buying second ticket.
        if conference.name in self.tickets:
            return

        # Cant consider too expensive conferences
        if conference.price > self.wealth:
            return

        # todo: move elsewhere
        if conference.start_date < self.model.date:
            return

        # Calculate distance penalty
        if conference.city == self.city:
            distance_penalty = 0
        else:
            distance = self.model.location_map[(
                self.city, conference.city)]
            distance_penalty = distance
        return distance_penalty

    def check_for_conferences(self):
        """Looks through all conferences. Calls `consider_buyingticket`"""

        if self.tickets:
            # We have tickets already no need to check
            return

        for conference in self.model.conferences:
            distance_penalty = self.assess_conference(conference)
            interest = self.calculate_interest_in_conference(conference)
            self.consider_buying_a_ticket(conference, interest, distance_penalty)

    def calculate_interest_in_conference(self, conference):
        """Calculates interest in conference based on how much topics fit"""
        interest = self.interest_matching_mode(
            conference.topics, self.interests)

        self._report_interest(interest)
        return interest

    def consider_buying_a_ticket(self, conference, interest: int, distance_penalty: float):
        interest -= distance_penalty / 10
        if interest < 45:
            return

        self.wealth -= conference.price
        conference.wealth += conference.price
        self.tickets.append(conference.name)
        conference.ticket_sold_count += 1
        self._report_purchase(conference)

    def work(self):
        """Work requires certain skill, there are other people working there too."""
        if not self.is_employed:
            return

    def look_for_job(self):
        """Look for a job"""
        if self.is_employed:
            return

        interesting_jobs = []  # todo: look for job in market
        if interesting_jobs:
            self.job = interesting_jobs[0]
            self.is_employed = True

    def collect_monthly_wage(self):
        """Collects monthly wage

        Todo: wage should be transfered to bank by employee
        Company, employee, account."""

        # Not employed, cannnot collect
        if not self.is_employed:
            return

        # Not a day I get paid.
        if self.model.date.day != 10:
            return

        amount = self.monthly_income

        self.wealth += amount
        self.model.economy.wealth -= amount

    def buy_food(self):
        expenses = self.daily_food_expenses
        self.wealth -= expenses
        self.model.economy.wealth += expenses

    def pay_taxes(self):
        if self.model.date.day != 1:
            return
        taxes = self.monthly_taxes
        self.wealth -= taxes
        self.model.economy.wealth -= taxes

    def attend_event(self):
        # If event is today, attend.
        # What will happen?
        pass

    def step(self):
        """Steps done in a day.

        A person does a lot of stuff in a daily routine. He or she wakes up, showers, eats breakfast,
        commutes to work"""

        # You need this to survive. You will spend some money on it.
        self.buy_food()
        # Work and get paid. Likely, you work for some particular company.
        self.work()
        # You did well, here is your money transfer.
        self.collect_monthly_wage()
        # No job, or your current one does not satisfy you? Look for another one.
        self.look_for_job()
        # You need to pay taxes, all of them.
        self.pay_taxes()

        # Here is outlier.
        self.check_for_conferences()
        # you have a ticket, why not attending?
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
        self.unique_id = unique_id
        self.model = model
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.price = price
        self.visibility = visibility or 0.1
        self.topics = topics
        self.wealth = wealth or 500
        self.ticket_sold_count = 0
        self.city = city
        self.tickets = []

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

    def advertise(self):
        """Advertise

        Todo:
            advertising should be more particular:
            post to facebook or google ads and then someone could actually see it"""
        r = 0.01  # growth rate / tick
        K = 1  # carrying capacity
        x = self.visibility
        x = x + r * x * (1 - x / K)
        self.visibility = x

    def publish_tickets(self):
        # Need publish date
        if False:
            for ticket in self.tickets:
                ticket.published = True

    def step(self):
        """Steps are made day"""

        # Advertise
        self.select_date()
        self.publish_cfp()
        self.advertise()
        self.publish_tickets()

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


class Economy(Agent):
    def __init__(self, unique_id, model, agent):
        self.unique_id = unique_id
        self.model = model
        self.wealth = 100000
