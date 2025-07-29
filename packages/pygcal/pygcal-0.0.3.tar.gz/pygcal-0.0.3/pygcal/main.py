"""
main entry point to the program
"""

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
    calendars_result = api.calendarList().list().execute()
    calendars = calendars_result.get("items", [])
    if not calendars:
        return
    for calendar in sorted(calendars, key=lambda cal: cal.get("summary")):
        summary = calendar.get("summary")
        print(f"{summary}")


@register_endpoint(
    description="Dump calendars in JSON format",
)
def calendars_dump() -> None:
    api = get_api()
    calendars_result = api.calendarList().list().execute()
    calendars = calendars_result.get("items", [])
    if not calendars:
        return
    print(json.dumps(calendars, indent=2))


@register_main(
    main_description=DESCRIPTION,
    app_name=APP_NAME,
    version=VERSION_STR,
)
def main():
    pylogconf.core.setup()
    ConfigRequest.app_name = APP_NAME
    ConfigRequest.scopes = SCOPES
    register_functions()
    config_arg_parse_and_launch()


if __name__ == "__main__":
    main()
