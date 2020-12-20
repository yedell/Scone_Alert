""" Get All Scone Data

This script fetches all Arizmendi Bakery scones of the day from their website,
and for each scone, gets the dates they were available.
All of this data is written to a JSON file.

User may provide specific date ranges to filter or a filepath to write JSON data
via parameters for the function get_all_scone_data().

Requirements:
  - python `requests` package -> pip3 install requests
  - python `pytz` package -> pip3 install pytz

"""

from email_script import PACIFIC_TZ, API_URL
import requests, json, time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry 
from datetime import datetime
from collections import defaultdict

# API_URL = "http://www.arizmendi-sanrafael.com/api/open/GetItemsByMonth"

def make_http_request(date_for_query:datetime) -> dict:
    """Makes HTTP GET request to API_URL for param date_for_query with retries & backoff
       - Returns JSON response data for queried date param
    """
    
    retry_strategy = Retry(
        total = 7,
        backoff_factor=1,
        status_forcelist=[429, 500, 503, 504]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("http://", adapter)

    month_year_str = date_for_query.strftime('%m-%Y')
    query = {"month": month_year_str, "collectionId": "55c92c3fe4b0837bc6c0a67b"}

    print(f"Fetching data for {month_year_str} ...", end="\r")

    response = http.get(url=API_URL, params=query, timeout=5)
    # Raises exception if response status has non-200 code
    response.raise_for_status()

    try:
        return response.json()

    except ValueError as err:
        print(f"Uh oh! Didn't receive JSON response from HTTP GET to URL: '{response.url}'")
        print("-"*45)
        print(response.text,"\n","-"*45,sep="")
        raise(err)

def merge_dicts(current_month_dict:dict, saved_json_file_dict:dict) -> dict:
    """Returns current_month_dict combined with saved_json_file_dict for directly writing to all_scone_data.json"""

    for key,value in current_month_dict.items():
        # if current_month_dict scone name (key) present in saved_json_file_dict, append date list (value)
        #  else insert [] and append date list
        saved_json_file_dict.setdefault(key, []).extend(value)
    
    return saved_json_file_dict

def reduce_json_dict(big_dict:dict) -> dict:
    """Given JSON/Dictionary creates reduced dictionary with only Title -> Date list mapping
       - Returns reduced dictionary
    """
    
    reduced_dict = defaultdict(list)

    for event in big_dict:
        time_in_ms = event["startDate"]
        date = PACIFIC_TZ.localize(datetime.fromtimestamp(time_in_ms / 1000))
        date_string = date.strftime("%m/%d/%Y")
        
        # Add date to list of dates for given key
        reduced_dict[event["title"].lower()].append(date_string)
    
    return reduced_dict

def get_all_scone_data(start_date=datetime(2015,8,1), end_date=datetime(2021,1,1), filepath="scraped_data.json"):
    """Gets all scone data from start_date (inclusive) to end_date (exclusive) and writes it to JSON file
       - start_date and end_date optional, if not provided gets data for all time
       - filepath param is path to JSON file for writing scraped data -> if not provided, creates and writes to file in current directory
    """

    if start_date < datetime(2015, 8, 1) or end_date > datetime(2021, 1, 1):
        raise ValueError(f"Illegal start/end date! start_date ({start_date.strftime('%m/%d/%Y')}) must be after 08/01/2015 and end_date ({end_date.strftime('%m/%d/%Y')}) must be before 01/01/2021.")

    print(f"Scraping scone data from {start_date.strftime('%m/%Y')} to {end_date.strftime('%m/%Y')}")
    count_num_months = 0

    start_time = time.time()

    # Create/clear JSON file for writing data
    with open(filepath, "w") as f:
        f.write(r"{}")
    
    print(f"Created/cleared JSON file -> '{filepath}'")

    while start_date < end_date:
        # # For testing in offline mode
        # data_for_this_month = json.load(open(r"C:\resp_december.json")) # List of calendar events for december

        data_for_this_month = make_http_request(start_date)

        filtered_data = reduce_json_dict(data_for_this_month)

        with open(filepath, "r+") as jsonFile:
            saved_json_file_data = json.load(jsonFile)

            data_to_write = merge_dicts(filtered_data, saved_json_file_data)

            jsonFile.seek(0)  # rewind to beginning of file
            json.dump(data_to_write, jsonFile, indent=2)
            
            # jsonFile.truncate() # deal with case that new data is smaller than previous data

        # increment month at end of loop to get data for next month
        start_date = datetime(start_date.year + int(start_date.month / 12), (int(start_date.month % 12) + 1), 1)
        count_num_months += 1
    
    print("\n")
    print("*"*45)
    print(f"Took {(time.time() - start_time):.2f} seconds to get data from {count_num_months} total months.")

if __name__ == "__main__":

    # start_date = datetime(2019,4, 1)
    # end_date = datetime(2019,7, 1)
    # get_all_scone_data(start_date, end_date)

    get_all_scone_data()
