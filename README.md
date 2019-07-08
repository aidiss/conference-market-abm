Conference Market ABM
======================

This agent-based model simulates conference market behaviour.

There are two main actors in play:

1. Persons interest in conference and its topics.
2. Conferences, especially at the same time.

Todo:

- [ ] Calculate conference visibility from social media/networks.
- [ ] Person to person interaction, invitations to conferences.

To run use:

```shell
python run.py {scenario_name}
```

Available scenarios:

- 2018
- 2019

Events for consideration:

Person.BuyConferenceTicket
Person.BrowseFacebook
Person.BrowseTwitter
Person.AssessConference

Conference.PublishTicket
Conference.OrderFacebookAdvertisment
Conference.OrderGoogleAdvertisment

Facebook.AdvertiseEvent

Google.AdvertiseEvent

Company.PostJobListing
Company.HireEmployee
Company.FireEmployee
Company.PayEmployeeSalary
