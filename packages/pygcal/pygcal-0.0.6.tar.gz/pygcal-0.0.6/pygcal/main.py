"""
main entry point to the program
"""

import os
import json
import pylogconf.core
from pygooglehelper import register_functions, ConfigRequest, get_credentials
from pytconf import register_main, config_arg_parse_and_launch, register_endpoint
from googleapiclient.discovery import build

from pygcal.static import DESCRIPTION, APP_NAME, VERSION_STR
from pygcal.constants import SCOPES, API_SERVICE_NAME, API_VERSION


def get_api():
    ConfigRequest.scopes = SCOPES
    ConfigRequest.app_name = APP_NAME
    credentials = get_credentials()
    return build(
        serviceName=API_SERVICE_NAME,
        version=API_VERSION,
        credentials=credentials,
        cache_discovery=False,
    )


@register_endpoint(
    description="List calendars",
)
def calendars_list() -> None:
    api = get_api()
    all_calendars = []
    page_token = None
    while True:
        calendars_result = api.calendarList().list(pageToken=page_token).execute()
        all_calendars.extend(calendars_result.get("items", []))
        page_token = calendars_result.get("nextPageToken")
        if not page_token:
            break
    for calendar in sorted(all_calendars, key=lambda cal: cal.get("summary")):
        summary = calendar.get("summary")
        print(f"{summary}")


@register_endpoint(
    description="Dump calendars in JSON format",
)
def calendars_dump() -> None:
    api = get_api()
    all_calendars = []
    page_token = None
    while True:
        calendars_result = api.calendarList().list(pageToken=page_token).execute()
        all_calendars.extend(calendars_result.get("items", []))
        page_token = calendars_result.get("nextPageToken")
        if not page_token:
            break
    print(json.dumps(all_calendars, indent=2))


@register_endpoint(
    description="Show primary calendar name and id",
)
def show_primary_calendar() -> None:
    api = get_api()
    page_token = None
    while True:
        calendars_result = api.calendarList().list(pageToken=page_token).execute()
        for calendar_entry in calendars_result.get("items", []):
            is_primary = calendar_entry.get("primary", False)
            if is_primary:
                summary = calendar_entry.get("summary")
                calendar_id = calendar_entry.get("id")
                print(f"Name: [{summary}]")
                print(f"ID: [{calendar_id}]")
        page_token = calendars_result.get("nextPageToken")
        if not page_token:
            break


@register_main(
    main_description=DESCRIPTION,
    app_name=APP_NAME,
    version=VERSION_STR,
)
def main():
    pylogconf.core.setup()
    ConfigRequest.scopes = SCOPES
    ConfigRequest.location = os.path.dirname(os.path.realpath(__file__))
    register_functions()
    config_arg_parse_and_launch()


if __name__ == "__main__":
    main()
