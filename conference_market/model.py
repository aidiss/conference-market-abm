import datetime
import logging
from datetime import date
import os
import matplotlib.pyplot as plt
import pandas as pd
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation, StagedActivation

from conference_market.agents import Conference, Person
from conference_market.datacollector import datacollector
from conference_market.utils import daterange, timeit
from conference_market.agents import Facebook

REPORTING = False

@timeit
def create_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("log.log"),
            logging.StreamHandler()
        ])
    logger = logging.getLogger()
    return logger


logger = create_logger()


class ConferenceModel(Model):
    conferences = []

    def __init__(self, schedule=None, scenario=None):
        self.schedule = schedule or RandomActivation(self)
        # self.schedule = schedule or StagedActivation(self, stage_list=['step'], shuffle=True)
        self.datacollector = datacollector
        self.scenario = scenario
        self.facebook = Facebook(1, self)

    @timeit
    def build_scenario(self, person_count, conferences):
        self.location_map = {("kaunas", "vilnius"): 100,
                             ("vilnius", "kaunas"): 120}

        for i in range(person_count):
            person = Person.from_faker_profile(i, self)
            self.schedule.add(person)

        for i, c in enumerate(conferences):
            conference = Conference(i, self, **c)
            self.schedule.add(conference)
            # For agents to reach conference in easier way. Todo: should not be reached directly
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
        report_folder = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        logger.info("Collecting reports from datacollector")

        os.chdir('reports')
        os.mkdir(report_folder)
        os.chdir(report_folder)

        dc = self.datacollector

        # Model reporter
        model_vars_df = dc.get_model_vars_dataframe()

        # Agent reporter
        agent_vars_df = dc.get_agent_vars_dataframe()

        # Tables
        conferences = dc.get_table_dataframe("conferences")
        purchases = dc.get_table_dataframe("purchase")
        interests = dc.get_table_dataframe("interest")

        # Dumping
        logger.info("Dumping reports!")
        agent_vars_df.unstack()["wealth"].plot()
        plt.savefig("image.png")

        # Pickle
        conferences.to_pickle("conferences.p")
        purchases.to_pickle("purchase.p")
        interests.to_pickle("interest.p")

        # Html
        interests.to_html("interest.html")
        purchases.to_html("purchase_vars.html")
        agent_vars_df.to_html("agent_vars.html")
        model_vars_df.to_html("model_vars.html")

    @timeit
    def run(self):
        logger.info("Loading conferences!")
        logger.info("Building model!")
        person_count = self.scenario["agents"]["persons"]["count"]
        conferences = self.scenario["agents"]["conferences"]
        start_date = self.scenario["start_date"]
        end_date = self.scenario["end_date"]

        self.build_scenario(person_count=person_count, conferences=conferences)

        logger.info("Starting!")
        for single_date in daterange(start_date, end_date):
            self.date = single_date
            if single_date.day == 1:
                logger.info(single_date)
            self.step()

        logger.info("Steps completed!")
        logger.info("Finished!")
        self.report()
