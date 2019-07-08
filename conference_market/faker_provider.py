from faker import Faker
from faker.providers import BaseProvider

fake = Faker()


class ConferenceProvider(BaseProvider):
    conferences = ["one", "two", "three"]

    def conference(self):
        return dict(
            name=self.random_element(self.conferences),
            wealth=self.wealth(),
            start_date=self.start_date(),
            end_date=self.start_date(),
            price=self.price(),
            visibility=self.visibility(),
            topics=[self.topic() for _ in range(10)],
            city=self.city()
        )

    def wealth(self):
        return self.random_digit()

    def start_date(self):
        return fake.date()

    def end_date(self):
        return self.start_date() + 1

    def price(self):
        return self.random_int(30, 200)

    def visibility(self):
        return self.random_int()

    def topic(self):
        with open('conference_market/data/techs.txt') as f:
            data = f.read()
        return self.random_choices(data.split('\n'), length=1)[0]

    def city(self):
        self.random_choices({"Vilnius": .8, "Kaunas": .2})


fake.add_provider(ConferenceProvider)
