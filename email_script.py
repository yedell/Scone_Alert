"""

This script fetches Arizmendi Bakery scones of the day for this current month
from their website and stores the data in a dict.

Work in progress, will integrate with Google Calendar API for creating events.

Requirements:
  - python `requests` package -> pip3 install requests
  - python `pytz` package -> pip3 install pytz

"""

import requests, json, pytz
from datetime import datetime
from collections import defaultdict

API_URL = "http://www.arizmendi-sanrafael.com/api/open/GetItemsByMonth"
PACIFIC_TZ = pytz.timezone("America/Los_Angeles")

utc_now = pytz.utc.localize(datetime.utcnow())
pst_now = utc_now.astimezone(PACIFIC_TZ)
month_year_in_pst = pst_now.strftime('%m-%Y')

# TODO -> Move query inside function
api_query = {"month": month_year_in_pst, "collectionId": "55c92c3fe4b0837bc6c0a67b"}

def get_rest_data_this_month(url=None, filter_future=True):
    """Makes HTTP request to API_URL, goes through JSON list of calendar events/Scones for this month
       - Returns Dict of Scone types (key) -> Date (value)
    """

    if url:
        calendar_list = requests.get(url, params=api_query).json()
    else:
        # For testing in offline mode
        calendar_list = json.load(open(r"C:\resp_december.json")) # List of calendar events this month
    
    wanted_keys = ["startDate", "endDate", "publishOn", "urlId", "fullUrl"]
    filtered_dict = defaultdict(list)

    for day in calendar_list:
        # TODO: filter_future in separate function to not repeat code here
        time_in_ms = day["endDate"]
        date_end = PACIFIC_TZ.localize(datetime.fromtimestamp(time_in_ms / 1000))
        if filter_future:
            if date_end >= pst_now:
                item = {key:day[key] for key in wanted_keys}
                filtered_dict[day["title"].lower()].append(item)
        else:
            item = {key:day[key] for key in wanted_keys}
            filtered_dict[day["title"].lower()].append(item)

    return filtered_dict

# def reduce_list(data, )

#     # print(calendar_list[0])
#     # print("\n", calendar_list[20])

#     return filtered_dict


if __name__ == "__main__":
    # a = get_data_from_url()
    # desired_types = ["lemon"]

    # desired_set = set()
    # for ingredient in desired_types:
    #     for k,v in a.items():
    #         if ingredient in k:
    #             desired_set.add(k)

    # print(desired_set)

    print(get_rest_data_this_month(url=API_URL))


    # b = [k for k,v in a.items() if "raspberry" in k]
    # print(k)