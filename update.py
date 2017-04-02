__author__ = 'Florian Cassayre'

import datetime
import json
from twython import Twython


# Config

with open('config.json') as data_file:
    config = json.load(data_file)

now = datetime.datetime.now()

candidates = []

for event in config['events']:

    image = event['image']
    occurrence = event['occurrence']
    type = occurrence['type']

    if type == 'punctual':
        date_from = datetime.datetime.strptime(occurrence['from'], "%Y-%m-%d")
        date_to = datetime.datetime.strptime(occurrence['to'], "%Y-%m-%d") + datetime.timedelta(days=1)
        occurs = date_from <= now <= date_to

        priority = 0

    elif type == 'yearly':
        date_from = datetime.datetime.strptime(occurrence['from'], "%m-%d")
        date_to = datetime.datetime.strptime(occurrence['to'], "%m-%d") + datetime.timedelta(days=1)

        if date_from <= date_to:

            date_from = date_from.replace(year=now.year)
            date_to = date_to.replace(year=now.year)

            occurs = date_from <= now < date_to
        else:
            date_from = date_from.replace(year=now.year - 1)
            date_to = date_to.replace(year=now.year)

            occurs = date_from <= now < date_to

            if not occurs:
                date_from = date_from.replace(year=now.year)
                date_to = date_to.replace(year=now.year + 1)

                occurs = date_from <= now < date_to

        priority = 1

    elif type == 'monthly':
        occurs = int(occurrence['from']) <= now.day <= int(occurrence['to'])

        priority = 2

    else:
        raise RuntimeError()

    if occurs:
        candidates.append((priority, image))


best = None

for candidate in candidates:
    if best is None or candidate[0] < best[0]:
        best = candidate

if best is None:
    best = (0, config['default_image'])

# Twitter

with open('credentials.json') as data_file:
    credentials = json.load(data_file)['twitter']

twitter = Twython(credentials['app_key'], credentials['app_secret'], credentials['oauth_token'], credentials['oauth_token_secret'])


avatar = open('img/' + best[1] + '.png', 'rb')
twitter.update_profile_image(image=avatar)