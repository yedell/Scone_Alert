""" Main Script

This script fetches Arizmendi Bakery scones of the day for this current month
from their website and stores the data in a list. Can filter favorite scone
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
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime, timedelta
import google_calendar

BASE_URL = "http://www.arizmendi-sanrafael.com"
ENDPOINT = "/api/open/GetItemsByMonth"
API_URL = BASE_URL + ENDPOINT

PACIFIC_TZ = pytz.timezone("America/Los_Angeles")
UTC_NOW = pytz.utc.localize(datetime.utcnow())
PST_NOW = UTC_NOW.astimezone(PACIFIC_TZ)

class Event:
    def __init__(self, name, start_date, end_date, url):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.url = url
    
    def __repr__(self) -> str:
        return f"Event('{self.name}' on {self.start_date:%m/%d/%y})"

    def __str__(self) -> str:
        return f"{self.name} scone event - {self.start_date:%m/%d/%y}"

def make_http_request() -> dict:
    """Makes HTTP GET request to API_URL with retries & backoff
       - Returns JSON response data
    """
    month_year_in_pst = PST_NOW.strftime('%m-%Y')
    api_query = {"month": month_year_in_pst, "collectionId": "55c92c3fe4b0837bc6c0a67b"}

    
    retry_strategy = Retry(
        total = 4,
        backoff_factor=2,
        status_forcelist=[429, 500, 503, 504]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("http://", adapter)

    response = http.get(url=API_URL, params=api_query, timeout=10)
    response.raise_for_status() # Raises exception if status is non-200 code

    try:
        current_month_json = response.json()
        print("HTTP Request Success -> Retrieved Calendar Data")
        
        return current_month_json

    except ValueError as err:
        print(f"Uh oh! Didn't receive JSON response from HTTP request to URL: '{response.url}'")
        print("-"*45)
        print(response.text,"\n","-"*45,sep="")
        raise(err)


def get_rest_data_this_month(url=None, filter_future_events=True, filter_num_days_ahead=0) -> list:
    """Makes HTTP request to API_URL, goes through JSON list of calendar events/Scones for this month
       - url: optional, for running in 'online' mode with website URL
       - filter_future_events: optional, default only gets future events/disregards past events
       - filter_num_days_ahead: optional, gets events up to # of days in future
       - Returns List of Scone Event objects
    """

    if url:
        current_month_json = make_http_request()
    else: # For testing in offline mode
        # List of calendar events this month
        current_month_json = json.load(open(r"resp_december.json"))
    
    # Desired data we want to keep for each scone event/day 
    scone_event_list = []

    for event_day in current_month_json:
        # For each scone day, date is in unix epoch ms -> convert to PST
        event_end_time_in_ms = event_day["endDate"]
        event_date_end = PACIFIC_TZ.localize(datetime.fromtimestamp(event_end_time_in_ms / 1000))

        # Check if we want to only get future events and if this event is in future
        if not filter_future_events or event_date_end >= PST_NOW:
            event_start_time_in_ms = event_day["startDate"]
            event_date_start = PACIFIC_TZ.localize(datetime.fromtimestamp(event_start_time_in_ms / 1000))

            # Check if we only want events a certain # of days in future
            # -> i.e. if we only want events in the upcoming week
            if filter_num_days_ahead:
                if event_date_start > PST_NOW + timedelta(days=filter_num_days_ahead):
                    continue

            scone_event_list.append(
                Event(
                    name=event_day["title"].lstrip().rstrip(),
                    start_date=event_date_start, 
                    end_date=event_date_end, 
                    url=event_day["fullUrl"]
                )
            )

    return scone_event_list

def pretty_print_list(scone_event_list):
    """Pretty prints list of scone events"""
    for event in scone_event_list:
        print(f" - {event.name+':' :<40} {event.start_date.strftime('%m/%d/%y'):>1}")
    print("_"*60,"\n")

def filter_scones_inclusive(wanted_ingredients:list, scone_event_list:list) -> list:
    """Reduces scone event list to only contain scones with the ingredients we want;
       *INCLUSIVE* ingredients match, logical OR -> union of all ingredients
       - wanted_ingredients: list of ingredients in scones we want
       - scone_event_list: list of scone events
       - Returns list of scone event objects matching any desired ingredients
    """
    
    result = []
    for scone_event in scone_event_list:
        # Check if any of our wanted ingredients are in the scone name
        if any(
            ingredient.lower() in scone_event.name.lower() 
            for ingredient in wanted_ingredients
        ):
            
            result.append(scone_event)
    
    print(f"\nFound {len(result)} events with any ingredients: {wanted_ingredients}\n")
    pretty_print_list(result)

    return result
    # scone_list[:] = result

def filter_scones_exclusive(wanted_ingredients:list, scone_event_list:list) -> list:
    """Reduces scone event list to only contain scones with the ingredients we want;
       *EXCLUSIVE* ingredients match, logical AND -> intersection of all ingredients
       - wanted_ingredients: list of ingredients in scones we want
       - scone_event_list: list of scone events
       - Returns list of scone event objects matching all desired ingredients
    """

    result = []

    for scone_event in scone_event_list:
        # Check if all of our wanted ingredients are in the scone name
        if all(
            ingredient.lower() in scone_event.name.lower()
            for ingredient in wanted_ingredients
        ):

            result.append(scone_event)

    print(f"\nFound {len(result)} events with all ingredients: {wanted_ingredients}\n")
    pretty_print_list(result)

    return result
    # scone_list[:] = result

def create_calendar_events(scone_list:list):
    """Creates Google Calendar Events from given scone_list"""

    def capitalize(s):
        """Helper function to capitalize the first letter of every word"""
        s = ' '.join(word[0].upper() + word[1:] for word in s.split())
        return s
    
    preorder_url = r"https://arizmendi-4th-street.square.site/product/scone-of-the-day/88"

    for event in scone_list:

        relative_end = event.start_date + timedelta(hours=3)
        hours = f"Hours: {event.start_date.hour%12} {event.start_date:%p} - {event.end_date.hour%12} {event.end_date:%p}"

        event_template = {
            'summary': capitalize(event.name) + " Scone @ Arizmendi",
            'location': 'Arizmendi Bakery & Cafe, San Rafael, CA, USA',
            'description': f'{hours}\n\n{BASE_URL}{event.url}\n\nPreorder:\n\n{preorder_url}\n\nAdded by Scone Alert',
            'start': {
                'dateTime': event.start_date.isoformat(),
                'timeZone': event.start_date.tzinfo.zone,
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
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 20 * 60},
                {'method': 'popup', 'minutes': 5}
                ],
            },
        }

        service = google_calendar.main()
        calendar_event = service.events().insert(calendarId='primary', body=event_template).execute()

        print(f"New Calendar Event created: {calendar_event.get('htmlLink')}")


if __name__ == "__main__":

    scone_event_list = get_rest_data_this_month(url=API_URL)
    
    ingredients = ["raspberry", "chocolate"]

    scone_event_list = filter_scones_exclusive(ingredients, scone_event_list)

    create_calendar_events(scone_event_list)
