"""
helpers.py
Helper functions for date conversions, formatting, and utilities.
"""
from datetime import datetime

def iso_to_datetime(iso_str):
    """
    Convert ISO 8601 string to datetime object.
    Args:
        iso_str (str): ISO 8601 formatted string.
    Returns:
        datetime: Python datetime object.
    """
    return datetime.fromisoformat(iso_str)

def format_event(event):
    """
    Format a Google Calendar event for display or processing.
    Args:
        event (dict): Google Calendar event object.
    Returns:
        dict: Formatted event details.
    """
    return {
        'summary': event.get('summary'),
        'start': event['start'].get('dateTime', event['start'].get('date')),
        'end': event['end'].get('dateTime', event['end'].get('date'))
    }
