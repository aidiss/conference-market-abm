import yaml
import csv
from datetime import timedelta, date
import time

def load_techs():
    with open('conference_market/techs.txt') as f:
        techs = f.read().split('\n')
        techs = [x.lower() for x in techs]
    return techs


def load_yaml_scenario(path: str):
    with open('scenarios/%s.yaml' % path) as f:
        data = yaml.load(f)
    return data


def load_stackshare_techs():
    l = []
    with open('conference_market/stackshare_tech_dump_with_vote_count.csv') as f:
        data = [tech for tech, votes in csv.reader(f)]
    return data


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result
    return timed