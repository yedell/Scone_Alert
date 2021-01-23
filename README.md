# Scone Alert

A service that gets daily specials from [Arizmendi Bakery](http://www.arizmendi-sanrafael.com/daily-specials-1 "Daily Specials - Arizmendi Bakery") and notifies you when your favorite scones are available by creating events on your Google Calendar.

## Overview

I firmly believe Arizmendi's Raspberry Chocolate Chip Scone to be among the greatest pastries ever created by humankind. Unfortunately I am not alone in this belief, as it—along with many other daily scones Arizmendi offers—regularly sells out within hours of them opening. 

Instead of manually checking their daily scone calendar every few days and tracking the next time my favorite/elusive scone will be offered, I realized I could automate this process.

`main_script.py` - gets the current month's daily scone offerings & creates Google Calendar Events when your desired scones will be available. Designed to be run on a recurring schedule with [`crontab`](https://man7.org/linux/man-pages/man5/crontab.5.html) or a similar program.

## Dependencies

- **Python 3.6** or higher
- [requests](https://github.com/psf/requests)
- [pytz](https://pypi.org/project/pytz/)
- [Google API Client](https://github.com/googleapis/google-api-python-client)
- [google-auth-httplib2](https://github.com/googleapis/google-auth-library-python-httplib2)
- [google-auth-oauthlib](https://github.com/googleapis/google-auth-library-python-oauthlib)

```
$ pip install requests pytz google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Getting Started

To use the Google Calendar functionality, you will need authorize access to your Google account. This is accomplished by downloading a `credentials.json` file here:

https://developers.google.com/calendar/quickstart/python

Follow these steps: 

1. Click the **Enable the Google Calendar API** button
2. Enter a project name (I'd suggest naming it *Scone Alert* but it's unimportant) > hit **Next**
3. On *Configure your OAuth Client*, select *Desktop App* and hit **Create**
4. Click **Download Client Configuration** and make sure the now downloaded `credentials.json` file is in this project's directory

## Todo List

- :heavy_plus_sign: Add unit tests
- :heavy_plus_sign: Add `argparse` to run/input arguments on command line
- :white_check_mark: Add exclusive ingredients match (to only get scone that contains several ingredients) -> intersection vs union
- :heavy_plus_sign: Implement fuzzy matching for misspellings and permutations
- :white_check_mark: Clean up/refactor code (create Event class instead of dicts) & harden requests
- :heavy_plus_sign: Port to Google Apps Script
