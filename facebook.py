import datetime
import typing


class FacebookEvent:
    def __init__(
        self,
        name: str,
        host,
        description: str = None,
        start_datetime: datetime.datetime = None,
        end_datetime: datetime.datetime = None,
    ):
        self.name = name
        self.host = host
        self.description = description or ''
        self.attending = []
        self.admins = []
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

    def __repr__(self):
        return "Facebook event"
