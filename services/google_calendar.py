from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os, pickle
from config.settings import GOOGLE_CREDENTIALS_JSON_PATH
from ai_scheduler import generate_study_schedule
from datetime import datetime, timedelta, time, timezone
import pytz
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google():
    """Authenticate with Google Calendar API using OAuth2 credentials."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_JSON_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service= build('calendar', 'v3', credentials=creds)
    return service 

def get_events(service, calendar_id='primary', days_ahead=1):
    """Fetch upcoming events from Google Calendar"""
    now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    end_time = (datetime.utcnow() + timedelta(days=days_ahead)).replace(tzinfo=timezone.utc).isoformat()

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now,
        timeMax=end_time,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events


def get_free_slots(events, date=None, tz="UTC"):
    """Return list of free (start, end) tuples in given day, timezone-aware"""
    timezone_local = pytz.timezone(tz)
    if date is None:
        date = datetime.now(timezone_local).date()

    day_start = timezone_local.localize(datetime.combine(date, time.min))
    day_end = timezone_local.localize(datetime.combine(date, time.max))

    parsed_events = []
    for event in events:
        start_str = event['start'].get('dateTime')
        end_str = event['end'].get('dateTime')

        if start_str.endswith("Z"): start_str = start_str.replace("Z", "+00:00")
        if end_str.endswith("Z"): end_str = end_str.replace("Z", "+00:00")

        start_dt = datetime.fromisoformat(start_str)
        end_dt = datetime.fromisoformat(end_str)

        # Ensure timezone-aware in UTC
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)

        parsed_events.append((start_dt, end_dt))

    # Sort events by start time
    parsed_events.sort(key=lambda e: e[0])

    free_slots = []
    last_end = day_start.astimezone(timezone.utc)

    for event_start, event_end in parsed_events:
        event_start = event_start.astimezone(timezone.utc)
        event_end = event_end.astimezone(timezone.utc)

        if event_start > last_end:
            free_slots.append((last_end, event_start))

        last_end = max(last_end, event_end)

    if last_end < day_end.astimezone(timezone.utc):
        free_slots.append((last_end, day_end.astimezone(timezone.utc)))

    return free_slots


def add_sessions_to_calendar(service, schedule, calendar_id='primary'):
    """Add AI-generated study sessions to Google Calendar, skip overlapping events"""
    if not schedule:
        print("No sessions to add.")
        return

    # Fetch existing events for conflict checking
    existing_events = get_events(service, calendar_id=calendar_id, days_ahead=1)
    busy_times = []
    for ev in existing_events:
        start_str = ev['start'].get('dateTime')
        end_str = ev['end'].get('dateTime')
        if start_str.endswith("Z"): start_str = start_str.replace("Z", "+00:00")
        if end_str.endswith("Z"): end_str = end_str.replace("Z", "+00:00")
        busy_times.append((
            datetime.fromisoformat(start_str).replace(tzinfo=timezone.utc),
            datetime.fromisoformat(end_str).replace(tzinfo=timezone.utc)
        ))

    for session in schedule:
        start = datetime.fromisoformat(session["start"])
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        end = datetime.fromisoformat(session["end"])
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)

        # Skip if overlaps with any busy event
        if any(busy_start < end and start < busy_end for busy_start, busy_end in busy_times):
            print(f"Skipped: {session['topic']} (conflict with existing event)")
            continue

        event = {
            "summary": f"Study: {session['topic']}",
            "start": {"dateTime": start.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end.isoformat(), "timeZone": "UTC"},
        }

        try:
            service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f"Added: {session['topic']} from {session['start']} to {session['end']}")
        except Exception as e:
            print(f"Failed to add session {session}: {e}")

if __name__ == "__main__":
    service = authenticate_google()
    events = get_events(service)
    free_slots = get_free_slots(events)

    duration_minutes = 50
    break_minutes = 10
    # topics should be a list of dicts as expected by ai_scheduler
    topics = [{
        "name": "math",
        "difficulty": "medium",
        "deadline": "2025-08-30"
    },
    {
         "name": "Data Structures",
        "difficulty": "medium",
        "deadline": "2025-08-30"
    }
    ]
    days=1
    study_sessions = generate_study_schedule(free_slots, duration_minutes, break_minutes, topics, days)
    add_sessions_to_calendar(service, study_sessions, calendar_id='primary')

