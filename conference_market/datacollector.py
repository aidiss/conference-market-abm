from mesa.datacollection import DataCollector

datacollector = DataCollector(
    model_reporters={
        "agent_count": lambda m: m.schedule.get_agent_count(),
        "with_tickets": lambda m: len(
            [x for x in m.schedule.agents if len(x.__dict__.get("tickets", [])) != 0]
        ),
    },
    agent_reporters={"wealth": lambda a: a.wealth},
    tables={
        "Purchase": ["unique_id", "wealth", "conference_name", "date"],
        "interest": ["unique_id", "interest", "date"],
        "conferences": ["unique_id", "name", "ticket_sold_count", "date"],
    },
)
