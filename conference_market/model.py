import datetime
import logging
from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation, StagedActivation

from conference_market.agents import Conference, Economy, Person
from conference_market.datacollector import datacollector
from conference_market.utils import daterange, timeit


@timeit
def create_logger():
    logging.basicConfig(level='INFO')
    logger = logging.getLogger(__name__)
    return logger


logger = create_logger()

class ConferenceModel(Model):
    conferences = []

    def __init__(self, schedule=None, scenario=None):
        self.schedule = schedule or RandomActivation(self)
        # self.schedule = schedule or StagedActivation(self, stage_list=['step'], shuffle=True)
        self.datacollector = datacollector
        self.scenario = scenario

    @timeit
    def build_scenario(self, person_count, conferences):
        economy = Economy(9999, self)
        self.schedule.add(economy)
        self.economy = economy
        self.location_map = {('kaunas', 'vilnius'): 100, ('vilnius', 'kaunas'): 120}

        for i in range(person_count):
            person = Person.from_faker_profile(i, self)
            self.schedule.add(person)

        for i, c in enumerate(conferences):
            conference = Conference(i, self, **c)
            self.schedule.add(conference)
            self.conferences.append(conference)

        # conference = Conference.from_faker_conference(i, self)
        self.schedule.add(conference)

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def __repr__(self):
        return str(self.__class__.__name__)

    @timeit
    def report(self):
        logger.info('Collecting reports from datacollector')
        data = [x.__dict__ for x in self.schedule.agents]
        df = pd.DataFrame(data)
        agent_vars_df = self.datacollector.get_agent_vars_dataframe()
        model_vars_df = self.datacollector.get_model_vars_dataframe()
        table_vars_df = self.datacollector.get_table_dataframe('Purchase')
        print(self.datacollector.get_table_dataframe('Purchase'))
        print(self.datacollector.get_table_dataframe('conferences'))
        self.datacollector.get_table_dataframe(
            'interest').to_html('reports/interest.html')
        self.datacollector.get_table_dataframe(
            'interest').to_pickle('reports/interest.p')
        self.datacollector.get_table_dataframe(
            'conferences').to_pickle('reports/conferences.p')
        agent_vars_df.unstack()['wealth'].plot()
        plt.savefig('reports/image.png')

        logger.info('Dumping reports!')
        agents_report_path = 'reports/agent_vars.html'
        agent_vars_df.to_html(agents_report_path)
        model_report_path = 'reports/model_vars.html'
        model_vars_df.to_html(model_report_path)
        model_vars_report_path = 'reports/purchase_vars.html'
        table_vars_df.to_html(model_vars_report_path)

    def run(self):
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
            if single_date.day == 1:
                print(single_date)
            self.step()

        logger.info('Steps completed!')
        logger.info('Finished!')
        self.report()
