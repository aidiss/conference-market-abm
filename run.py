import argparse

from conference_market.model import ConferenceModel
from conference_market.utils import load_yaml_scenario


def create_argument_parser():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-s", "--scenario", required=True)
    return argument_parser


def run():
    argument_parser = create_argument_parser()
    args = argument_parser.parse_args()

    scenario_name = args.scenario
    scenario = load_yaml_scenario(scenario_name)

    m = ConferenceModel(scenario=scenario)
    m.run()


if __name__ == "__main__":
    run()
