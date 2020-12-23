""" Google Calendar Service

https://developers.google.com/calendar/quickstart/python

Taken from Google Calendar API Quickstart Guide.
Must have credentials.json file in same directory, get from above link. 
Script attempts to open browser and requests access permission from Google Account.
Stores authorization in pickle file so subsequent runs won't ask again.

Requirements:
  - google-api-python-client 
  - google-auth-httplib2 
  - google-auth-oauthlib

pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib

"""

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    """Authenticates with Google Calendar API
       - Returns Calendar service
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

if __name__ == '__main__':
    # main()
    pass