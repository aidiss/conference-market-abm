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
    conferences = ['one', 'two', 'three']

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
        return 'asd'


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
        self.city = choice(['kaunas', 'vilnius', 'vilnius'])

    @classmethod
    def from_faker_profile(cls, unique_id, model):
        return cls(unique_id, model, **fake.profile())

    def check_for_conferences(self):
        for conference in self.model.conferences:

            # Did person see the conference
            if conference.visibility < self.awareness:
                continue

            # Do not consider buying second ticket.
            if conference.name in self.tickets:
                continue

            # Cant consider too expensive conferences
            if conference.price > self.wealth:
                continue

            # todo: move elsewhere
            if conference.start_date < self.model.date:
                continue

            if conference.city == self.city:
                distance_penalty = 0
            else:
                distance = self.model.location_map[(
                    self.city, conference.city)]
                distance_penalty = distance

            interest = self.calculate_interest_in_conference(conference)
            self.consider_buying_a_ticket(
                conference, interest, distance_penalty)

    def calculate_interest_in_conference(self, conference):
        interest = self.interest_matching_mode(
            conference.topics, self.interests)

        # self.model.datacollector.add_table_row(
        #     table_name='interest',
        #     row={
        #         'unique_id': self.unique_id,
        #         'interest': interest,
        #         'date': self.model.date
        #     }
        # )
        return interest

    def consider_buying_a_ticket(self, conference, interest, distance_penalty):
        interest -= distance_penalty / 10

        if interest > 45:
            self.wealth -= conference.price
            conference.wealth += conference.price
            self.tickets.append(conference.name)
            conference.ticket_sold_count += 1

            self.model.datacollector.add_table_row(
                table_name='Purchase',
                row={
                    'unique_id': self.unique_id,
                    'conference_name': conference.name,
                    'wealth': self.wealth,
                    'date': self.model.date
                }
            )

    def work(self):
        """Work requires certain skill, there are other people working there too."""
        pass

    def look_for_job(self):
        """Look for a job"""
        interesting_jobs = []
        if interesting_jobs:
            self.job = interesting_jobs[0]
            self.is_employed = True

    def collect_monthly_wage(self, source, amount):
        self.wealth += amount
        source.wealth -= amount

    def buy_food(self):
        expenses = self.daily_food_expenses
        self.wealth -= expenses
        self.model.economy.wealth += expenses

    def pay_taxes(self):
        taxes = self.monthly_taxes
        self.wealth -= taxes
        self.model.economy.wealth -= taxes

    def step(self):
        """Steps done in a day.

        A person does a lot of stuff in a daily routine. He or she wakes up, showers, eats breakfast,
        commutes to work"""

        self.buy_food()

        if self.is_employed:
            self.work()
            if self.model.date.day == 10:
                self.collect_monthly_wage(
                    source=self.model.economy, amount=self.monthly_income)
        else:
            self.look_for_job()

        # I dont have any tickets, what should I do?
        if not self.tickets:
            self.check_for_conferences()

        # for ticket in self.tickets:
        #     if self.check_if_conference_is_today(ticket):
        #         self.attend(ticket.conference)

        # Pay taxes
        if self.model.date.day == 1:
            self.pay_taxes()

    def __repr__(self):
        return str(self.__class__.__name__) + str(self.__dict__)


class Conference:
    def __init__(
            self,
            unique_id: int,
            model: Model,
            name: str,
            start_date: datetime,
            end_date: datetime,
            price: str,
            visibility: float,
            topics: List[str],
            wealth: int,
            city: str):
        self.unique_id = unique_id
        self.model = model
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.price = price
        self.visibility = visibility or 0.1
        self.topics = topics
        self.wealth = 500
        self.ticket_sold_count = 0
        self.city = city

    @classmethod
    def from_faker_conference(cls, unique_id, model, **kwargs):
        return cls(unique_id, model, **fake.conference())

    def __repr__(self):
        return str(self.__class__.__name__) + str(self.__dict__)

    def advertise(self):
        r = .01  # growth rate / tick
        K = 1  # carrying capacity
        x = self.visibility
        x = x+r*x*(1-x/K)
        self.visibility = x

    def dump_report(self):
        self.model.datacollector.add_table_row(
            table_name='conferences',
            row={
                'unique_id': self.unique_id,
                'name': self.name,
                'ticket_sold_count': self.ticket_sold_count,
                'date': self.model.date
            }
        )

    def step(self):
        # Advertise
        # Sign a speaker
        # Publish tickets
        # Increase visibility
        self.advertise()
        self.dump_report()


class Economy(Agent):
    def __init__(self, unique_id, agent):
        self.unique_id = unique_id
        self.wealth = 100000
