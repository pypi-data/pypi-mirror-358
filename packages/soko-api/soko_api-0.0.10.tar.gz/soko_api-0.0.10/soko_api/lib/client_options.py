from typing import Any, Callable, Dict, Optional, Union

from httpx import Timeout
from postgrest.constants import DEFAULT_POSTGREST_CLIENT_TIMEOUT


class ClientOptions:

    def __init__(self):
        self.schema: str = "public"

        self.headers: Dict[str, str] = {}

        self.auto_refresh_token: bool = True
        """Automatically refreshes the token for logged in users."""

        self.persist_session: bool = True
        """Whether to persist a logged in session to storage."""

        self.postgrest_client_timeout: Union[
            int, float, Timeout
        ] = DEFAULT_POSTGREST_CLIENT_TIMEOUT
        """Timeout passed to the SyncPostgrestClient instance."""
