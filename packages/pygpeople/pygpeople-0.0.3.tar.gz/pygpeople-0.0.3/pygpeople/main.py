"""
main
"""
import os.path
import json

import pylogconf.core
from pygooglehelper import register_functions, ConfigRequest, get_credentials
from pytconf import register_endpoint, register_main, config_arg_parse_and_launch
from googleapiclient.discovery import build

from pygpeople.static import APP_NAME, DESCRIPTION, VERSION_STR
from pygpeople.constants import SCOPES, API_SERVICE_NAME, API_VERSION


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
    configs=[],
    description="Get my profile data",
)
def me() -> None:
    api = get_api()
    results = api.people().get(
        resourceName="people/me",
        personFields="names,emailAddresses"
    ).execute()
    print(json.dumps(results, indent=2))


@register_endpoint(
    configs=[],
    description="Get all my contacts in JSON format",
)
def contacts_json() -> None:
    api = get_api()
    all_contacts = []
    page_token = None
    page_counter = 1

    while True:
        results = (
            api.people()
            .connections()
            .list(
                resourceName="people/me",
                pageSize=1000,
                personFields="names,emailAddresses,phoneNumbers,organizations,biographies",
                pageToken=page_token,
            )
            .execute()
        )
        connections = results.get("connections", [])
        all_contacts.extend(connections)
        page_token = results.get("nextPageToken")
        if not page_token:
            break
        page_counter += 1
    print(json.dumps(all_contacts, indent=2))


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
