"""Context class for keeping track of the conversation state in Redis."""

from typing import Any

from redis import asyncio as redis

from lego.lego_types import JSONDict, Messages
from lego.models import ReprEnum
from lego.settings import RedisConnection


class RedisContext:
    """
    Redis conversation context.

    RedisContext includes three main components:
    - state: for storing the conversation state.
    - export: for storing data that will be exported to a frontend.
    - messages: for storing the conversation history.

    Each component can be pulled with the corresponding method:
    - `state()`
    - `export()`
    - `messages()`

    'state' is a dictionary that stores the information extracted/generated
    during the conversation. Accessing and updating the state is done through
    the `set_`, `get`, `del`, and `count` methods. The latter allows to
    increment a counter under a specific key.

    'export' is a place where to aggregate data that will be sent to somewhere
    outside the backend. Adding to the export is done by setting a key-value
    pair with the `set_` method and specifying the `export` parameter as True.

    'messages' is list designed to store the conversation history. One assumes
    that the messages are dicts with string keys and string values of the same
    format as OpenAI's ChatGPT. There are `last_message` and `save_message`
    methods to access and update the message history.
    """

    def __init__(self, conversation_id: str, connection: RedisConnection):
        self.redis = redis.from_url(connection.url())
        ## It may be a better option to use the following instead
        ## since no need to use urllib.parse.unquote_plus?
        # self.redis = redis.Redis(
        #     host=connection.host,
        #     port=connection.port,
        #     db=connection.db,
        #     password=connection.password,
        # )
        self.redon = self.redis.json()
        self.convid = conversation_id

    async def init(self) -> None:
        """
        Initialize the conversation context.

        Creates the three essential keys in the database:
        - state: for storing the conversation state.
        - export: for storing data that will be exported to a frontend.
        - messages: for storing the conversation history.
        """
        await self.redon.set(self.convid, "$", {}, nx=True)
        await self.redon.set(self.convid, "$.state", {}, nx=True)
        await self.redon.set(self.convid, "$.export", {}, nx=True)
        await self.redon.set(self.convid, "$.messages", [], nx=True)

    async def session_info(self) -> tuple[str, str, float] | None:
        """
        Return the session info.

        Returns: (access_token, session_id, expires_in_Xseconds) tuple.
        """
        ## FIXME: unpacking tuple needs too much caution.
        if not (session_id := await self.get("session_id")):
            return None

        if not (token := await self.get("access_token")):
            raise KeyError("Access token is missing.")

        return token, session_id, await self.redis.ttl(self.convid)

    async def set_session(
        self, access_token: str, session_id: str, expires_in: float
    ):
        """
        Set the session info.

        Args:
            :param access_token: The access token for OAuth2.0 authentication.
            :param session_id: The session ID to distinguish among sessions.
            :param expires_in: The expiration time in seconds. Will be rounded
                to the nearest integer.
        """
        await self.set_("session_id", session_id)
        await self.set_("access_token", access_token)
        await self.redis.expire(self.convid, int(expires_in))

    async def state(self) -> JSONDict:
        """Return info extracted during the conversation."""
        res = await self.redon.get(self.convid, "$.state")
        return res[0]

    async def export(self) -> JSONDict:
        """Return what was registered for export."""
        res = await self.redon.get(self.convid, "$.export")
        return res[0]

    async def messages(self) -> Messages:
        """Return the conversation history."""
        res = await self.redon.get(self.convid, "$.messages")
        return res[0]

    async def set_(
        self,
        key: str | ReprEnum,
        value: Any,  # type: ignore[misc]
        export: bool = False,
        list_append: bool = False,
        add_to_dict: str | None = None,
    ):
        """
        Set a key-value pair in the conversation state.

        Args:
            :param key: The key to set the value.
            :param value: The value to set.
            :param export: Whether to add the key-value pair to export dict.
        """
        if list_append:
            if (potential_list := await self.get(key)) is None:
                await self.redon.set(self.convid, f"$.state.{key}", [])
            elif not isinstance(potential_list, list):
                raise ValueError(f"Not a list under the key {key}.")
            await self.redon.arrappend(self.convid, f"$.state.{key}", value)
        elif add_to_dict:
            if (potential_dict := await self.get(add_to_dict)) is None:
                await self.redon.set(self.convid, f"$.state.{add_to_dict}", {})
            elif not isinstance(potential_dict, dict):
                raise ValueError(f"Not a dict under the key {add_to_dict}.")
            await self.redon.set(
                self.convid, f"$.state.{add_to_dict}.{key}", value
            )
        else:
            await self.redon.set(self.convid, f"$.state.{key}", value)

        if export:
            if list_append or add_to_dict:
                raise ValueError(
                    "Appending to a list or adding to a dict"
                    " during export is not allowed."
                )
            await self.redon.set(self.convid, f"$.export.{key}", value)

    async def count(self, key: str | ReprEnum) -> int:
        """Update the counter under the `key`."""
        if counter := await self.get(key):
            if not isinstance(counter, int):
                raise TypeError("Counter is not an integer.")
        else:
            await self.set_(key, 1)
        res = await self.redon.numincrby(self.convid, f"$.state.{key}", 1)  # type: ignore[no-untyped-call]
        return res[0]

    async def get(  # type: ignore[misc]
        self, key: str | ReprEnum, fallback_value: Any = None
    ) -> Any:
        """Get a key-value pair from the conversation state."""
        result = await self.redon.get(self.convid, f"$.state.{key}")
        return result[0] if result else fallback_value

    async def del_(self, key: str | ReprEnum):
        """
        Delete a key-value pair from the conversation state.

        If the key is not found, it will do nothing.
        """
        if await self.get(key):
            await self.redon.delete(self.convid, f"$.state.{key}")

    async def save_message(self, message: dict[str, str]):
        """Append a message to the conversation history list."""
        await self.redon.arrappend(self.convid, "$.messages", message)  # type: ignore[misc]

    async def last_message(self) -> dict[str, str]:
        """Return the last message in the conversation history."""
        if result := await self.redon.get(self.convid, "$.messages[-1]"):
            return result[0]
        raise IndexError("Empty message history.")

    async def close(self):
        """Close the Redis connection."""
        await self.redis.aclose()
