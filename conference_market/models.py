import datetime

from facebook import FacebookEvent


class JobPosting:
    def __init__(self, name, description, company):
        self.name = name
        self.description = description
        self.company = company


class FacebookEventAdvertisment:
    def __init__(self, event: FacebookEvent, payer, budget: int, end_date=datetime.datetime):
        self.event = event
        self.payer = payer
        self.budget = budget
        self.end_date = end_date
