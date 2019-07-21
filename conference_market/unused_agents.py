class Conference:
    def publish_tickets(self):
        # Need publish date
        if not self.published_tickets:
            for ticket in self.tickets:
                ticket.published = True

    def advertise_facebook(self):
        """Advertise"""

        r = 0.01  # growth rate / tick
        K = 1  # carrying capacity
        x = self.visibility
        x = x + r * x * (1 - x / K)
        self.visibility = x
# self.advertise()
# self.publish_tickets()


# Agent
class Person:

    def assess_conference(self, conference):
        # Did person see the conference
        if conference.visibility < self.awareness:
            return

        # Do not consider buying second ticket.
        if conference.name in self.tickets:
            return

        # Cant consider too expensive conferences
        if conference.price > self.wealth:
            return

        # todo: move elsewhere
        if conference.start_date < self.model.date:
            return

        return True

    def assess_conference_topic(self, conference):
        import Levenshtein
        interests = self.interests
        description = conference.description

        if isinstance(interests, list):
            interests = '. '.join(interests)
        if isinstance(description, list):
            description = '. '.join(description)

        distance = Levenshtein.distance(interests, description)

        return distance

    def check_for_conferences(self):
        """Looks through all conferences. Calls `consider_buyingticket`"""

        if self.tickets:
            # We have tickets already no need to check
            return

        for conference in self.model.conferences:
            if not self.assess_conference(conference):
                continue

            # Calculate distance penalty
            if conference.city == self.city:
                distance_penalty = 0
            else:
                distance = self.model.location_map[(
                    self.city, conference.city)]
                distance_penalty = distance

            interest = self.calculate_interest_in_conference(conference)
            self.consider_buying_a_ticket(
                conference, interest, distance_penalty)

    def consider_buying_a_ticket(self, conference, interest: int, distance_penalty: float):
        interest -= distance_penalty / 10
        if interest < 45:
            return

        self.buy_conference_ticket(conference)

    def work(self):
        """Work requires certain skill, there are other people working there too."""
        if not self.is_employed:
            return

    def look_for_job(self):
        """Look for a job"""
        interesting_jobs = []  # todo: look for job in market
        if interesting_jobs:
            self.job = interesting_jobs[0]
            self.is_employed = True

    def collect_monthly_wage(self):
        """Collects monthly wage

        Todo: wage should be transfered to bank by employee"""
        amount = self.monthly_income

        self.wealth += amount

    def buy_food(self):
        expenses = self.daily_food_expenses
        self.wealth -= expenses

    def pay_taxes(self):
        taxes = self.monthly_taxes
        self.wealth -= taxes

    def browse_job_postings(self, job_posting_site: JobPostingSite):
        """By browsing a site you increase your interest in certain technologies"""
        for job_posting in job_posting_site.job_postings:
            job_posting.description

    def calculate_interest_in_conference(self, conference):
        """Calculates interest in conference based on how much topics fit"""

        # Very slow. Todo: need to replace with faster approach
        interest = self.interest_matching_mode(
            conference.topics, self.interests)

        if REPORTING:
            self._report_interest(interest)
        return interest

    def step(self):
        # You need this to survive. You will spend some money on it.
        self.buy_food()

        # Work and get paid. Likely, you work for some particular company.
        if self.is_employed:
            self.work()

        # You did well, here is your money transfer.
        if self.is_employed and (self.model.date.day == 10):
            self.collect_monthly_wage()

        # No job, or your current one does not satisfy you? Look for another one.
        if not self.is_employed:
            self.look_for_job()

        # You need to pay taxes, all of them.
        if self.model.date.day == 1:
            self.pay_taxes()

        # Here is outlier.
        if not self.tickets:
            self.check_for_conferences()
