from services.google_calendar import authenticate_google, get_events
import datetime

svc = authenticate_google()
# get calendar metadata
cal = svc.calendars().get(calendarId='primary').execute()
print('Calendar summary:', cal.get('summary'), 'ID:', cal.get('id'))

# list events for next 7 days
now = datetime.datetime.utcnow().isoformat() + 'Z'
end = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat() + 'Z'

events_result = svc.events().list(calendarId='primary', timeMin=now, timeMax=end, singleEvents=True, orderBy='startTime').execute()
events = events_result.get('items', [])
print('Found', len(events), 'events in next 7 days')
for e in events:
    summary = e.get('summary','(no summary)')
    start = e['start'].get('dateTime') or e['start'].get('date')
    endt = e['end'].get('dateTime') or e['end'].get('date')
    print('-', summary, '|', start, '->', endt, '| id:', e.get('id'))

# show Study Session matches
print('\nStudy Session matches:')
for e in events:
    if 'study session' in e.get('summary','').lower():
        print('-', e.get('summary'), e['start'].get('dateTime') or e['start'].get('date'), e.get('id'))
