import yaml
import csv
from datetime import timedelta, date


def load_techs():
    with open('conference_tickets/techs.txt') as f:
        techs = f.read().split('\n')
        techs = [x.lower() for x in techs]
    return techs


def load_yaml_scenario(path: str):
    with open('scenarios/%s.yaml' % path) as f:
        data = yaml.load(f)
    return data


def load_stackshare_techs():
    l = []
    with open('conference_tickets/stackshare_tech_dump_with_vote_count.csv') as f:
        data = [tech for tech, votes in csv.reader(f)]
    return data


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)
