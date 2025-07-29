import json
import mimetypes
import re
from typing import Dict, Union, Any

import requests
from httpx import Timeout
from postgrest import SyncPostgrestClient, SyncRequestBuilder, SyncFilterRequestBuilder
from postgrest.constants import DEFAULT_POSTGREST_CLIENT_TIMEOUT

from .lib.client_options import ClientOptions


class SupabaseException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class Client:

    def __init__(
            self,
            api_url: str,
            soko_api_key: str,
            options: ClientOptions = ClientOptions(),
    ):
        if not api_url:
            raise SupabaseException("api_url is required")
        if not soko_api_key:
            raise SupabaseException("soko_api_key is required")

        # Check if the url and key are valid
        if not re.match(r"^(https?)://.+", api_url):
            raise SupabaseException("Invalid URL")

        # Check if the key is a valid JWT
        if not re.match(
                r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$", soko_api_key
        ):
            raise SupabaseException("Invalid API key")

        self.api_url = api_url
        self.soko_api_key = soko_api_key
        self.user_api_key = None
        self.access_token = None
        self.refresh_token = None
        self.current_user = None

        options.headers.update(self._get_auth_headers())

        self.rest_url: str = f"{api_url}/rest/v1"
        self.auth_url: str = f"{api_url}/auth/v1"
        self.storage_url = f"{api_url}/storage/v1"

        self.postgrest = self._init_postgrest_client(
            rest_url=self.rest_url,
            supabase_key=self.soko_api_key,
            headers=options.headers,
            schema=options.schema,
            timeout=options.postgrest_client_timeout,
        )

    def sign_up(
            self, email: str, password: str, data: dict
    ):
        signin_request = requests.post("{}/signup".format(self.auth_url), json={
            "email": email,
            "password": password,
            "data": data
        }, headers={
            'apiKey': self.soko_api_key
        })

        signin_response = None
        if signin_request.status_code == 200:
            signin_response = json.loads(signin_request.content)
        else:
            signin_response = json.loads(signin_request.content)

        return signin_response

    def sign_in_with_password(
            self, email: str, password: str
    ):
        login_request = requests.post("{}/token?grant_type=password".format(self.auth_url), json={
            "email": email,
            "password": password
        }, headers={
            'apiKey': self.soko_api_key,
            'Authorization': 'Bearer {}'.format(self.soko_api_key)
        })

        login_response = None
        if login_request.status_code == 200:
            login_response = json.loads(login_request.content)
            # use this user as logged user in postgrest
            self.postgrest.auth(token=login_response.get('access_token'))
            self.access_token = login_response.get('access_token')
            self.refresh_token = login_response.get('refresh_token')
            self.current_user = login_response.get('user')

        return login_response

    def sign_in_with_jwt(
            self, jwt: str
    ):
        user_request = requests.get("{}/user".format(self.auth_url), headers={
            'apiKey': self.soko_api_key,
            'Authorization': 'Bearer {}'.format(jwt)
        })

        user_response = None
        if user_request.status_code == 200:
            user_response = json.loads(user_request.content)
            # use this user as logged user in postgrest
            self.postgrest.auth(token=jwt)
            self.access_token = jwt
            # one time login without refresh function
            # self.refresh_token = login_response.get('refresh_token')
            self.current_user = user_response

        return user_response

    def sign_in_with_api_key(
            self, api_key: str
    ):
        # use User Personal API KEY

        options: ClientOptions = ClientOptions()
        options.headers.update(self._get_auth_headers())
        options.headers.update({
            "userApiKey": api_key
        })

        self.user_api_key = api_key

        self.postgrest = self._init_postgrest_client(
            rest_url=self.rest_url,
            supabase_key=self.soko_api_key,
            headers=options.headers,
            schema=options.schema,
            timeout=options.postgrest_client_timeout,
        )

    @staticmethod
    def _init_postgrest_client(
            rest_url: str,
            supabase_key: str,
            headers: Dict[str, str],
            schema: str,
            timeout: Union[int, float, Timeout] = DEFAULT_POSTGREST_CLIENT_TIMEOUT,
    ) -> SyncPostgrestClient:
        """Private helper for creating an instance of the Postgrest client."""
        client = SyncPostgrestClient(
            rest_url, headers=headers, schema=schema, timeout=timeout
        )
        client.auth(token=supabase_key)
        return client

    def _get_auth_headers(self) -> Dict[str, str]:
        """Helper method to get auth headers."""
        # What's the corresponding method to get the token
        return {
            "apiKey": self.soko_api_key,
            "Authorization": f"Bearer {self.soko_api_key}",
        }

    def table(self, table_name: str) -> SyncRequestBuilder:
        """Perform a table operation.

        Note that the supabase client uses the `from` method, but in Python,
        this is a reserved keyword, so we have elected to use the name `table`.
        Alternatively you can use the `.from_()` method.
        """
        return self.from_(table_name)

    def from_(self, table_name: str) -> SyncRequestBuilder:
        """Perform a table operation.

        See the `table` method.
        """
        return self.postgrest.from_(table_name)

    def rpc(self, fn: str, params: Dict[Any, Any]) -> SyncFilterRequestBuilder:
        """Performs a stored procedure call.

        Parameters
        ----------
        fn : callable
            The stored procedure call to be executed.
        params : dict of any
            Parameters passed into the stored procedure call.

        Returns
        -------
        SyncFilterRequestBuilder
            Returns a filter builder. This lets you apply filters on the response
            of an RPC.
        """
        return self.postgrest.rpc(fn, params)

    def upload_thumbnail(
            self,
            file,
            entity_id
    ):
        mime = mimetypes.guess_type(file)

        files = {
            "file": (
                entity_id,
                open(file, "rb"),
                mime[0]
            )
        }

        res = requests.post("{}/object/thumbnails/{}".format(self.storage_url, entity_id), headers={
            'apiKey': self.soko_api_key,
            'Authorization': 'Bearer {}'.format(self.access_token if self.access_token else self.soko_api_key)
        }, files=files)

        return res

    def upload_file(
            self,
            bucket,
            file,
            entity_id
    ):
        mime = mimetypes.guess_type(file)

        files = {
            "file": (
                entity_id,
                open(file, "rb"),
                mime[0]
            )
        }

        res = requests.post("{}/object/{}/{}".format(self.storage_url, bucket, entity_id), headers={
            'apiKey': self.soko_api_key,
            'userApiKey': self.user_api_key,
            'Authorization': 'Bearer {}'.format(self.access_token if self.access_token else self.soko_api_key)
        }, files=files)

        return res

    def delete_files(self, bucket, ids):

        res = requests.delete(
            "{}/object/{}".format(self.storage_url, bucket),
            headers={
                'apiKey': self.soko_api_key,
                'Authorization': 'Bearer {}'.format(self.access_token if self.access_token else self.soko_api_key)
            },
            json={"prefixes": ids}
        )

        return res


def create_client(
        api_url: str,
        soko_api_key: str,
        options: ClientOptions = ClientOptions(),
) -> Client:
    return Client(api_url=api_url, soko_api_key=soko_api_key, options=options)
