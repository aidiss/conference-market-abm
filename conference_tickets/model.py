from datetime import date
import datetime
import matplotlib.pyplot as plt
import logging

import pandas as pd

from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from conference_tickets.agents import Conference, Person, Economy
from conference_tickets.utils import daterange


def create_logger():
    logging.basicConfig(level='INFO')
    logger = logging.getLogger(__name__)
    return logger


logger = create_logger()


class ConferenceModel(Model):
    conferences = []

    def __init__(self, schedule=None, scenario=None):
        self.schedule = schedule or RandomActivation(self)
        self.datacollector = DataCollector(
            model_reporters={
                "agent_count": lambda m: m.schedule.get_agent_count(),
                "with_tickets": lambda m: len([x for x in m.schedule.agents if len(x.__dict__.get('tickets', [])) != 0])},
            agent_reporters={"wealth": lambda a: a.wealth},
            tables={"Purchase": ["unique_id", "wealth", 'conference_name','date']},

        )
        self.scenario = scenario

    def build_scenario(self, person_count, conferences):
        economy = Economy(9999, self)
        self.schedule.add(economy)
        self.economy = economy

        for i in range(person_count):
            person = Person(i, self)
            self.schedule.add(person)

        for i, c in enumerate(conferences):
            conference = Conference(i, self, visibility=0.1, **c)
            self.schedule.add(conference)
            self.conferences.append(conference)

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def __repr__(self):
        return str(self.__class__.__name__)

    def report(self):
        data = [x.__dict__ for x in self.schedule.agents]
        df = pd.DataFrame(data)
        agent_vars_df = self.datacollector.get_agent_vars_dataframe()
        model_vars_df = self.datacollector.get_model_vars_dataframe()
        table_vars_df = self.datacollector.get_table_dataframe('Purchase')

        agent_vars_df.unstack()['wealth'].plot()
        plt.savefig('reports/image.png')

        agent_vars_df.to_html('reports/agent_vars.html')
        model_vars_df.to_html('reports/model_vars.html')
        table_vars_df.to_html('reports/purchase_vars.html')

    def run(self, steps):
        logger.info('Loading conferences!')
        logger.info('Building model!')
        person_count = self.scenario['agents']['persons']['count']
        conferences = self.scenario['agents']['conferences']
        start_date = self.scenario['start_date']
        end_date = self.scenario['end_date']

        self.build_scenario(person_count=person_count, conferences=conferences)

        logger.info('Starting!')
        for single_date in daterange(start_date, end_date):
            self.date = single_date
            self.step()

        logger.info(f'{steps} steps completed!')
        logger.info('Finished!')
        self.report()
