#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# NCP Engineering GmbH

import logging
_logger = logging.getLogger(__name__)

# try imports to avoid exceptions when `NcpSemApi` is imported.
# Exceptions will only be thrown when the specific class is used.
try:
    from asyncio import get_running_loop, run
    asyncio_available = True

    import platform
    if platform.system()=='Windows':
        from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())
except (ModuleNotFoundError, ImportError):
    asyncio_available = False
    get_running_loop, run = None, None

# using oktas python library: https://github.com/okta/okta-sdk-python
try:
    from okta.client import Client
    okta_available = True
except ModuleNotFoundError:
    okta_available = False
    Client = None


class OktaQueryParams:
    """Class to bundle parameters for oktas `list_users` api call.

    Attributes:
        Described here:
        users:
            https://developer.okta.com/docs/reference/api/users/#request-parameters-3
        groups:
            https://developer.okta.com/docs/reference/api/groups/#list-groups
        users_in_group:
            https://developer.okta.com/docs/reference/api/groups/#list-group-members

    """
    def __init__(self,
                 limit: str = None,
                 search: str = None,
                 sortBy: str = None,
                 sortOrder: str = None):
        self.limit: str = limit
        self.search: str = search
        self.sortBy: str = sortBy
        self.sortOrder: str = sortOrder

    def as_dict(self) -> dict:
        """Return query parameters as dictionary.

        Returns:
            dict: Dictionary containing *only the set* query paramters.
        """
        if self.sortBy and not self.search:
            _logger.warning("'sortBy' is supported for search queries only")
        if self.sortOrder and not self.search:
            _logger.warning("'sortOrder' is supported for search queries only")
        query_params = {}
        for param in ('limit', 'search', 'sortBy', 'sortOrder'):
            attr = getattr(self, param)
            if attr:
                query_params[param] = attr
        return query_params


class Okta:
    """Okta REST API Class for querying registered users.

    To obtain a token navigate to your Okta dashboard and click on
    `Security -> API` in the left-hand menu.
    Tokens can then be created from the `Tokens`-Tab by clicking on
    `Create token`.
    The domain can be obtained from the profile information in the top right
    section of the Okta dashboard and needs to contain the 'https://' prefix.
    For example: 'https://dev-123456.okta.com'

    More info here:
    https://developer.okta.com/docs/guides/create-an-api-token/main/

    Attributes:
        token (str): Okta API token
        domain (str): `https` prefixed Okta Domain
            example: 
    """
    def __init__(self, token: str, domain: str) -> None:
        if not okta_available:
            raise ModuleNotFoundError(
                    "Okta library not available! "
                    "Try installing it with 'pip install okta'.")
        if not asyncio_available:
            raise ModuleNotFoundError(
                    "Asyncio library not available! "
                    "Please ensure you have Python version 3.7 "
                    "or later installed or install it with "
                    "'pip install asyncio'.")

        config = {
            'orgUrl': domain,
            'token': token
        }
        self.client = Client(config)

    async def list_users_async(
                self, query_params: OktaQueryParams = None) -> list:
        """List all users asyncronously.

        Arguments:
            query_params (OktaQueryParams), optional: object containing
                the desired query parameters.
                Supported attributes: all

        Returns:
            List containing all found users.
        """
        all_users = []
        query_params = query_params.as_dict() if query_params else {}

        users, resp, err = await self.client.list_users(query_params)
        while True:
            if err:
                _logger.error(err.message)
                return []
            if users:
                all_users += users
            if resp.has_next():
                users, err = await resp.next()
            else:
                break
        return [user.as_dict() for user in users]

    def list_users(self, query_params: OktaQueryParams = None) -> list:
        """List all users syncronously.

        This method simply synchronises the `list_users_async` call.

        Arguments:
            query_params (OktaQueryParams): object holding the desired
                query parameters.
                Supported attributes: all

        Returns:
            List containing all found users.
        """
        return self._synchronize(self.list_users_async,
                                 query_params)

    async def list_groups_async(
                self, query_params: OktaQueryParams = None) -> list:
        """List all groups asyncronously.

        Arguments:
            query_params (OktaQueryParams), optional: object containing
                the desired query parameters.
                Supported attributes: all

        Returns:
            List containing all found groups.
        """
        all_groups = []
        query_params = query_params.as_dict() if query_params else {}

        groups, resp, err = await self.client.list_groups(query_params)
        while True:
            if err:
                _logger.error(err.message)
                return []
            if groups:
                all_groups += groups
            if resp.has_next():
                groups, err = await resp.next()
            else:
                break
        return [group.as_dict() for group in groups]

    def list_groups(self, query_params: OktaQueryParams = None) -> list:
        """List all groups syncronously.

        This method simply synchronises the `list_groups_async` call.

        Arguments:
            query_params (OktaQueryParams): object holding the desired
                query parameters.
                Supported attributes: all

        Returns:
            List containing all found groups.
        """
        return self._synchronize(self.list_groups_async,
                                 query_params)
    
    async def list_users_in_group_async(self, group_id: str,
                                query_params: OktaQueryParams = None) -> list:
        """List all users in group $group_id asyncronously.

        Arguments:
            group_id (str): Group Id as obtained from list_groups_async.
            query_params (OktaQueryParams), optional: object containing
                the desired query parameters.
                Supported attributes: 'limit'

        Returns:
            List containing all found users.
        """
        all_users = []
        query_params = query_params.as_dict() if query_params else {}

        users, resp, err = await self.client.list_group_users(group_id, query_params)
        while True:
            if err:
                _logger.error(err.message)
                return []
            if users:
                all_users += users
            if resp.has_next():
                users, err = await resp.next()
            else:
                break
        return [user.as_dict() for user in users]

    def list_users_in_group(self, group_id: str,
                            query_params: OktaQueryParams = None) -> list:
        """List all users in group $group_id syncronously.

        This method simply synchronises the `list_users_in_group_async` call.

        Arguments:
            group_id (str): Group Id as obtained from list_groups_async.
            query_params (OktaQueryParams), optional: object containing
                the desired query parameters.
                Supported attributes: 'limit'

        Returns:
            List containing all found users.
        """
        return self._synchronize(self.list_users_in_group_async,
                                 group_id,
                                 query_params)
    
    def _synchronize(self, function, *args, **kwargs):
        """Synchronize the getter functions."""
        try:
            loop = get_running_loop()
        except RuntimeError:  # There is no current event loop...
            loop = None

        res = function(*args, **kwargs)
        if loop and loop.is_running():
            return loop.run_until_complete(res)
        return run(res)

if __name__ == "__main__":
    import argparse
    from pprint import pprint
    parser = argparse.ArgumentParser("Okta API examples")
    parser.add_argument("token", help="Okta API Token")
    parser.add_argument("domain", help="Okta Domain")
    args = parser.parse_args()

    client = Okta(args.token, args.domain)

    print("EXAMPLE #1: "
        "Getting the first 10 Active Users alphabetically by profile email:")
    query = OktaQueryParams(
        limit=10,
        search='status eq "ACTIVE"',
        sortBy='profile.email'
    )
    users = client.list_users(query)
    for user in users:
        pprint(user, indent=2)

    print("EXAMPLE #2: Getting all users")
    users = client.list_users()
    print(f"Total amount of users: {len(users)}")

    print("EXAMPLE #3: "
        "Getting id,description and name of all groups "
        "created after 2023-01-01:")
    query = OktaQueryParams(search='created gt "2023-01-01T00:00:00.000Z"')
    groups = client.list_groups(query)
    for group in groups:
        pprint({
            "id": group["id"],
            "description": group.get("profile", {}).get("description"),
            "name": group.get("profile", {}).get("name"),
        }, indent=2)

    print("EXAMPLE #4: Getting all groups and show as <id>: <name>")
    groups = client.list_groups()
    for group in groups:
        print(f"{group['id']}: {group.get('profile', {}).get('name')}")

    print("EXAMPLE #6: Getting all members of the first group")
    members = client.list_users_in_group(groups[0]['id'])
    for member in members:
        pprint(member)

    if asyncio_available:
        print("EXAMPLE #7: Using asyncio to use the async methods:")

        async def list_all_users_groups_asynchronously(client: Okta):
            """This simply show how the async methods can be used.
            
            It is not in itself asynchronous,
            first get the users, then the groups.
            """
            users = await client.list_users_async()
            groups = await client.list_users_async()
            return {'users': users, 'groups': groups}
        
        from asyncio import run
        result = run(list_all_users_groups_asynchronously(client))
        pprint(result)
