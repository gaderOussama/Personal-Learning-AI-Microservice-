# ensure project root is on sys.path so local package imports resolve
import importlib.util, sys, os, datetime
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# load services/google_calendar.py as a module
path = os.path.join(project_root, 'services', 'google_calendar.py')
path = os.path.abspath(path)
spec = importlib.util.spec_from_file_location('svc_google_calendar', path)
mod = importlib.util.module_from_spec(spec)
# execute module
spec.loader.exec_module(mod)

svc = mod.authenticate_google()
cal = svc.calendars().get(calendarId='primary').execute()
print('Calendar summary:', cal.get('summary'), 'ID:', cal.get('id'))

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

print('\nStudy Session matches:')
for e in events:
    if 'study session' in e.get('summary','').lower():
        print('-', e.get('summary'), e['start'].get('dateTime') or e['start'].get('date'), e.get('id'))
