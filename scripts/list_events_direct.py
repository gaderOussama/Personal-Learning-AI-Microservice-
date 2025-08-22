"""
Direct read-only script to authenticate and list calendar events without importing project modules.
"""
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os, pickle, datetime

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CRED_PATH = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', 'token.pickle')

creds = None
if os.path.exists(TOKEN_PATH):
    with open(TOKEN_PATH, 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CRED_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
    with open(TOKEN_PATH, 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)
cal = service.calendars().get(calendarId='primary').execute()
print('Calendar summary:', cal.get('summary'), 'ID:', cal.get('id'))

now = datetime.datetime.utcnow().isoformat() + 'Z'
end_time = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat() + 'Z'
res = service.events().list(calendarId='primary', timeMin=now, timeMax=end_time, singleEvents=True, orderBy='startTime').execute()
events = res.get('items', [])
print('Found', len(events), 'events in next 7 days')
for e in events:
    summary = e.get('summary','(no summary)')
    start = e['start'].get('dateTime') or e['start'].get('date')
    endt = e['end'].get('dateTime') or e['end'].get('date')
    print('-', summary, '|', start, '->', endt, '| id:', e.get('id'))

print('\nStudy Session matches:')
for e in events:
    if 'study session' in e.get('summary','').lower():
        print('-', e.get('summary'), e['start'].get('dateTime') or e['start'].get('date'), e.get('id'))
