#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# NCP Engineering GmbH

import logging
from enum import Enum
from typing import Iterator
_logger = logging.getLogger(__name__)

# using azures msal python library:
# https://github.com/AzureAD/microsoft-authentication-library-for-python
try:
    from msal import ConfidentialClientApplication
    azure_available = True
except ModuleNotFoundError:
    azure_available = False
    ConfidentialClientApplication = None

try:
    import requests
    requests_available = True
except ModuleNotFoundError:
    requests_available = False

class AzureQueryParams:
    """Class to bundle parameters for azures `list users` api call.

    Usage:
        parameters = AzureQueryParams(
            select='deviceId,displayName,registrationDateTime',
            filter="createdDateTime ge 2024-01-01T12:00:00Z")

    Attributes:
        Described here:
        https://docs.microsoft.com/en-us/graph/query-parameters#odata-system-query-options
        Available parameters:
        $expand, $filter, $orderBy, $select, $search and $top
    """
    def __init__(self,
                 expand: str = None,
                 filter: str = None,
                 orderBy: str = None,
                 select: str = None,
                 search: str = None) -> None:
        self.expand: str = expand
        self.filter: str = filter
        self.orderBy: str = orderBy
        self.search: str = search
        self.select: str = select

    def as_dict(self) -> dict:
        """Return query parameters as dict formatted as azure expects it.

        Returns:
            dict: Dictionary containing *only the set* query paramters.
        """
        query_params = {}
        for param in ('expand', 'filter', 'orderBy', 'search', 'select'):
            attr = getattr(self, param)
            if attr and param == "search" and attr[0] != '"':
                # Quote the search string if it is not quoted already
                query_params[f'${param}'] = f'"{attr}"'
            elif attr:
                query_params[f'${param}'] = attr
        return query_params


class Azure:
    """Azure REST API Class for querying users.

    To obtain the client secret, an application needs to be created first
    inside your azure tenant under `App registrations`.
    From there generate a client secret in `Certificates & secrets`.

    `Client_id` and `authority` can be obtained from the applicatons overview
    page.

    Additionally, the app needs to be given the following permissions,
    which can be added under `API permissions` of the created applicaion:
    - `User.Read.All`   (to list users)
    - `Device.Read.All` (to list devices)
    - `GroupMember.Read.All` (to list groups and members)

    A redirect url is not needed.

    Attributes:
        client_id (str): Azure AD Application (client) ID
        client_secret (str): Azure AD Applicaitons Client secret
        authority (str): Azure AD Directory (tenant) ID
        api_url (str, optional): Custom API url
    """
    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 authority: str,
                 api_url: str = "https://graph.microsoft.com") -> None:
        if not azure_available:
            raise ModuleNotFoundError(
                    "Azure `msal` library not available! "
                    "Try installing it with 'pip install msal'.")

        if not requests_available:
            raise ModuleNotFoundError(
                    "`requests` library not available! "
                    "Try installing it with 'pip install requests'.")

        self.token = None
        self.scope = ["https://graph.microsoft.com/.default"]
        self.api_url = api_url

        self.app = ConfidentialClientApplication(client_id,
                                                client_secret,
                                                authority)

    class MemberRole(Enum):
        USER = "/microsoft.graph.user"
        DEVICE = "/microsoft.graph.device"
        ANY = ""

    def list_users(self,
                   query_params: AzureQueryParams = None,
                   is_advanced_query = False) -> Iterator[dict]:
        """List users present in the Azure AD directory.

        Required permissions: `User.Read.All`

        Arguments:
            query_params (AzureQueryParams, optional): object holding the
                desired query parameters.
            is_advanced_query (bool, optional): Signal advanced query.
                Required when using the `search` query paramater.
                This results in the `ConsistencyLevel` header added with value set to `eventual`.
                See more about advanced queries here:
                https://learn.microsoft.com/en-us/graph/aad-advanced-queries?tabs=python

        Returns:
            Iterator[dict]: An iterator over the dictionaries of the found users.
        See:
            https://learn.microsoft.com/en-us/graph/api/user-list
        """
        self._authenticate()
        endpoint = f"{self.api_url}/v1.0/users"
        query_args = query_params.as_dict() if query_params else {}
        authentication_header = {'Authorization': 'Bearer ' + self.token}
        return self._get_pagination_data(endpoint=endpoint,
                                         headers=authentication_header,
                                         query_args=query_args,
                                         is_advanced_query=is_advanced_query)

    def list_devices(self, query_params: AzureQueryParams = None,
                   is_advanced_query = False) -> Iterator[dict]:
        """List devices present in the Azure AD directory.

        Required permissions: `Device.Read.All`

        Arguments:
            query_params (AzureQueryParams, optional): object holding the
                desired query parameters.
            is_advanced_query (bool, optional): Signal advanced query.
                Required when using the `search` query paramater.
                This results in the `ConsistencyLevel` header added with value set to `eventual`.
                See more about advanced queries here:
                https://learn.microsoft.com/en-us/graph/aad-advanced-queries?tabs=python

        Returns:
            Iterator[dict]: An iterator over the dictionaries of the found devices.
        See:
            https://learn.microsoft.com/en-us/graph/api/device-list
        """
        self._authenticate()
        endpoint = f"{self.api_url}/v1.0/devices"
        query_args = query_params.as_dict() if query_params else {}
        authentication_header = {'Authorization': 'Bearer ' + self.token}
        return self._get_pagination_data(endpoint=endpoint,
                                         headers=authentication_header,
                                         query_args=query_args,
                                         is_advanced_query=is_advanced_query)

    def list_groups(self, query_params: AzureQueryParams = None,
                    is_advanced_query = False) -> Iterator[dict]:
        """List groups present in the Azure AD directory.

        Required permissions: `GroupMember.Read.All`

        Arguments:
            query_params (AzureQueryParams, optional): object holding the
                desired query parameters.
            is_advanced_query (bool, optional): Signal advanced query.
                Required when using the `search` query paramater.
                This results in the `ConsistencyLevel` header added with value set to `eventual`.
                See more about advanced queries here:
                https://learn.microsoft.com/en-us/graph/aad-advanced-queries?tabs=python

        Returns:
            Iterator[dict]: An iterator over the dictionaries of the found groups.
        See:
            https://learn.microsoft.com/en-us/graph/api/group-list
        """
        self._authenticate()
        endpoint = f"{self.api_url}/v1.0/groups"
        query_args = query_params.as_dict() if query_params else {}
        authentication_header = {'Authorization': 'Bearer ' + self.token}
        return self._get_pagination_data(endpoint=endpoint,
                                         headers=authentication_header,
                                         query_args=query_args,
                                         is_advanced_query=is_advanced_query)

    def list_group_members(self,
                           group_id: str,
                           role: MemberRole = MemberRole.USER,
                           query_params: AzureQueryParams = None,
                           is_advanced_query = False) -> Iterator[dict]:
        """List group members present in the Azure AD directory.

        Required permissions: `GroupMember.Read.All`

        Arguments:
            group_id (str): Id of the group.
            role (MemberRole): Role of the group memebers.
                               Can be a user, device or any role.
                               Default is user.
            query_params (AzureQueryParams, optional): object holding the
                desired query parameters.
            is_advanced_query (bool, optional): Signal advanced query.
                Required when using the `search` query paramater.
                This results in the `ConsistencyLevel` header added with value set to `eventual`.
                See more about advanced queries here:
                https://learn.microsoft.com/en-us/graph/aad-advanced-queries?tabs=python

        Returns:
            Iterator[dict]: An iterator over the dictionaries of the found members.
        See:
            https://learn.microsoft.com/en-us/graph/api/group-list
        """
        self._authenticate()
        endpoint = f"{self.api_url}/v1.0/groups/{group_id}/members{role.value}"
        query_args = query_params.as_dict() if query_params else {}
        authentication_header = {'Authorization': 'Bearer ' + self.token}
        return self._get_pagination_data(endpoint=endpoint,
                                         headers=authentication_header,
                                         query_args=query_args,
                                         is_advanced_query=is_advanced_query)

    def _authenticate(self) -> str:
        """Authenticate with Azure by aquiring a token."""
        if self.token:
            _logger.debug("Token already set")
            return

        # Firstly, looks up a token from cache
        # Since we are looking for token for the current app,
        # NOT for an end user,
        # notice we give account parameter as None.
        result = self.app.acquire_token_silent(self.scope, account=None)
        if not result:
            result = self.app.acquire_token_for_client(scopes=self.scope)

        if 'access_token' not in result:
            _logger.error(
                f"{result.get('error')}: {result.get('error_description')}")
            raise AzureAuthenticationTokenMissingError()
        self.token = result['access_token']

    def _get_pagination_data(self,
                             endpoint: str,
                             headers: dict,
                             query_args: dict,
                             is_advanced_query: bool) -> Iterator[dict]:

        if is_advanced_query:
            headers["ConsistencyLevel"] = "eventual"

        response = requests.get(endpoint,
                                headers=headers,
                                params=query_args).json()
        while True:
            if 'error' in response:
                _logger.error(f"{response['error']['code']}: "
                    f"{response['error']['message']}")
                break

            for value in response.get('value', []):
                yield value

            if '@odata.nextLink' in response:
                _logger.debug(f"Getting next page from {response['@odata.nextLink']}")
                response = requests.get(response['@odata.nextLink'],
                                        headers=headers).json()
            else:
                break


class AzureAuthenticationTokenMissingError(Exception):
    # Define the template in Unicode to accommodate possible Unicode variables
    msg = u'Could not obtain a valid token'

    def __init__(self, *args, **kwargs):
        super(AzureAuthenticationTokenMissingError, self).__init__(self.msg.format(**kwargs), *args)
        self.kwargs = kwargs


if __name__ == "__main__":
    import argparse
    from pprint import pprint

    parser = argparse.ArgumentParser("Azure Graph API demo")
    parser.add_argument("id", help="Azure Apps Client ID")
    parser.add_argument("secret", help="Azure Apps Client secret")
    parser.add_argument(
        "authority",
        help="Azure Ad Authority Uri, typically of form "
             "https://login.microsoftonline.com/Your_Tenant_ID")
    args = parser.parse_args()

    client = Azure(args.id,
                   args.secret,
                   args.authority)

    print("EXAMPLE #1: "
        "Getting the first 10 Users alphabetically by displayName:")
    users = client.list_users(AzureQueryParams(
            select='displayName',
            orderBy='displayName'))
    # The _ in the for loop simply dismisses the counter variable.
    # It is not needed.
    # The loop is stepped through 10 times and each time the next result
    # from the `list_users` query is retrieved by calling `next(users)`.
    # Once the list is empty, the next call will raise a `StopIteration`
    # exception.
    for _ in range(10):
        try:
            pprint(next(users), indent=2)
        except StopIteration:
            print("No more users...")
            break

    print("EXAMPLE #2: Getting all users")
    # Now instead of using a for loop to get the first 10 users we use
    # a so called list comprehension to get all the users and save them
    # to an array.
    users = [user for user in client.list_users()]
    print(f"Total amount of users: {len(users)}")

    print("EXAMPLE #3: "
        "Getting deviceId,displayName,registrationDateTime of all devices "
        "created after 2024-01-01T12:00:00Z:")
    parameters = AzureQueryParams(
            select='deviceId,displayName,registrationDateTime',
            filter="createdDateTime ge 2024-01-01T12:00:00Z")
    devices = client.list_devices(parameters)
    # Another example: Now we are using a for loop to iterate over the devices.
    # The benefit of this method compared to the one above with the list
    # comprehension is that the program returns the first device
    # as soon as it is available and it does not store all results in memory
    # (which can be very large depending on the amount of results)...
    # This method is the recomended one when operating on all users at once
    # is not required.
    for device in devices:
        pprint(device, indent=2)

    print("EXAMPLE #4: Getting all groups")
    groups = [g for g in client.list_groups()]
    for group in groups:
        print(f"{group['id']}: {group['displayName']}")

    print("EXAMPLE #5: Getting all devices of the first group")
    members = client.list_group_members(groups[0]['id'], Azure.MemberRole.DEVICE)
    for member in members:
        pprint(member)

    print("EXAMPLE #6: Getting all members of the second group")
    members = client.list_group_members(groups[1]['id'], Azure.MemberRole.ANY)
    for member in members:
        pprint(member)

    print("EXAMPLE #7: Search for users that have \"ncp\" in their Email")
    query = AzureQueryParams(search='"mail:ncp"')
    # We have to set `is_advanced_query=True` because we are using the `search`
    # query parameter.
    users = [user for user in client.list_users(query, is_advanced_query=True)]
    pprint(users)
