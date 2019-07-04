from mesa.datacollection import DataCollector

datacollector = DataCollector(
    model_reporters={
        "agent_count": lambda m: m.schedule.get_agent_count(),
        "with_tickets": lambda m: len(
            [x for x in m.schedule.agents if len(x.__dict__.get("tickets", [])) != 0]
        ),
    },
    # Only for info that is available for all
    agent_reporters={
        "wealth": lambda a: a.wealth,
        "monthly_income": lambda a: a.monthly_income if a.__dict__.get('monthly_income') else None,
        "is_employed": lambda a: a.is_employed if a.__dict__.get('is_employed') else None,
    },
    tables={
        "purchase": ["unique_id", "wealth", "conference_name", "date"],
        "interest": ["unique_id", "interest", "date"],
        "conferences": ["unique_id", "name", "ticket_sold_count", "date"],
    },
)
