""" Main Script

This script fetches Arizmendi Bakery scones of the day for this current month
from their website and stores the data in a dict. Can filter favorite scone
types and create Calendar events through Google Calendar API.

Work in progress.

Requirements:
  - python `requests` package
  - python `pytz` package
  - google-api-python-client
  - google-auth-httplib2
  - google-auth-oauthlib

pip3 install requests pytz google-api-python-client google-auth-httplib2 google-auth-oauthlib

"""

import requests, json, pytz
from datetime import datetime, timedelta
from collections import defaultdict
import google_calendar

BASE_URL = "http://www.arizmendi-sanrafael.com"
ENDPOINT = "/api/open/GetItemsByMonth"
API_URL = BASE_URL + ENDPOINT
PACIFIC_TZ = pytz.timezone("America/Los_Angeles")

utc_now = pytz.utc.localize(datetime.utcnow())
pst_now = utc_now.astimezone(PACIFIC_TZ)
month_year_in_pst = pst_now.strftime('%m-%Y')

# TODO -> Move query inside function
api_query = {"month": month_year_in_pst, "collectionId": "55c92c3fe4b0837bc6c0a67b"}

def get_rest_data_this_month(url=None, filter_future_events=True, filter_num_days_ahead=0) -> defaultdict:
    """Makes HTTP request to API_URL, goes through JSON list of calendar events/Scones for this month
       - url : optional, for running in 'online' mode with website URL
       - filter_future_events : optional, default only gets future events/disregards past events
       - filter_num_days_ahead : optional, gets events up to # of days in future
       - Returns Dict of Scone types (key) -> {startDate, endDate, fullUrl} (value)
    """

    if url:
        current_month = requests.get(url, params=api_query).json()
    else:
        # For testing in offline mode
        current_month = json.load(open(r"C:\Scone_Alert\resp_december.json")) # List of calendar events this month
    
    # Desired data we want to keep for each scone event/day 
    # wanted_keys = ["startDate", "endDate", "publishOn", "urlId", "fullUrl"]
    scone_dict = defaultdict(list)

    for event_day in current_month:
        # For each scone day, date is in unix epoch ms -> convert to PST
        event_end_time_in_ms = event_day["endDate"]
        event_date_end = PACIFIC_TZ.localize(datetime.fromtimestamp(event_end_time_in_ms / 1000))

        # Check if we want to only get future events and if this event is in future
        if not filter_future_events or event_date_end >= pst_now:
            event_start_time_in_ms = event_day["startDate"]
            event_date_start = PACIFIC_TZ.localize(datetime.fromtimestamp(event_start_time_in_ms / 1000))

            # Check if we only want events a certain # of days in future
            # -> i.e. if we only want events in the upcoming week
            if filter_num_days_ahead:
                if event_date_start > pst_now + timedelta(days=filter_num_days_ahead):
                    continue

            event_dict = {
                "startDate" : event_date_start,
                "endDate"  : event_date_end,
                "fullUrl" : event_day["fullUrl"]
            }
            scone_dict[event_day["title"].lower()].append(event_dict)

            # item = {key:event_day[key] for key in wanted_keys}
            # filtered_dict[event_day["title"].lower()].append(item)

        # if filter_future:
        #     if date_end >= pst_now:
        #         item = {key:day[key] for key in wanted_keys}
        #         filtered_dict[day["title"].lower()].append(item)
        # else:
        #     item = {key:day[key] for key in wanted_keys}
        #     filtered_dict[day["title"].lower()].append(item)

    # if in_next_num_days:

    return scone_dict


def get_desired_scones(wanted_ingredients:list, scone_dict:defaultdict) -> dict:
    """Reduces scone dict to only contain scones with the ingredients we want
       - wanted_ingredients: list of ingredients in scones we want
       - scone_dict: dict of scones
       - Returns reduced scone dict
    """

    reduced_dict = {}

    for ingredient in wanted_ingredients:
        # Need to keep track of scones we add to account for overlap w/ other ingredients
        added_scones = []
        
        for scone in scone_dict:
            if ingredient in scone:
                reduced_dict[scone] = scone_dict[scone]
                # We're going to delete this scone from scone_dict
                added_scones.append(scone)
        
        # Must delete scone from scone_dict, otherwise might count again w/ other ingredient
        for key in added_scones: del scone_dict[key]

    return reduced_dict

def create_calendar_events(scone_dict:dict):
    """Creates Google Calendar Events from given scone_dict"""

    def capitalize(s):
        """Helper function to capitalize the first letter of every word"""
        s = ' '.join(word[0].upper() + word[1:] for word in s.split())
        return s
    
    for scone in scone_dict:
        for scone_event in scone_dict[scone]:

            relative_end = scone_event["startDate"] + timedelta(hours=3)
            hours = f"Hours: {scone_event['startDate'].strftime('%I%p')} - {scone_event['endDate'].strftime('%I%p')}"

            event_template = {
                'summary': capitalize(scone) + " Scone @ Arizmendi",
                'location': 'Arizmendi Bakery & Cafe, San Rafael, CA, USA',
                'description': f'{hours}\n\n{BASE_URL}{scone_event["fullUrl"]}\n\nAdded by Scone Alert',
                'start': {
                    'dateTime': scone_event["startDate"].isoformat(),
                    'timeZone': scone_event["startDate"].tzinfo.zone,
                },
                'end': {
                    'dateTime': relative_end.isoformat(),
                    'timeZone': relative_end.tzinfo.zone,
                },
                'colorId': "1",
                # 'attendees': [
                #     {'email': ''}
                # ],
                'transparency': 'transparent',
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                    {'method': 'email', 'minutes': 16 * 60},
                    {'method': 'popup', 'minutes': 10 * 60},
                    ],
                },
            }

            service = google_calendar.main()
            calendar_event = service.events().insert(calendarId='primary', body=event_template).execute()

            print(f"New Calendar Event created: {calendar_event.get('htmlLink')}")


if __name__ == "__main__":

    this_month = get_rest_data_this_month()
    
    desired_ingredients = ["raspberry"]

    favorite_scones = get_desired_scones(desired_ingredients, this_month)

    create_calendar_events(favorite_scones)

    # for scone in desired_set:
    #     for event in desired_set[scone]:
    #         s = event["endDate"]
    #         print("")