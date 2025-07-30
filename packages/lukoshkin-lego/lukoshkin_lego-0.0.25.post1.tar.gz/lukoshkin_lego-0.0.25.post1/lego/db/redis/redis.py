"""Context class for keeping track of the conversation state in Redis."""

import json
from typing import Any

from redis import asyncio as redis

from lego.models import ReprEnum
from lego.settings import RedisConnection


class NotSet:
    """Sentinel type for not set values."""


_sentinel = NotSet()


class LegoRedisError(Exception):
    """Base class for Lego Redis errors."""


class LegoRedisMissingContextError(LegoRedisError):
    """Error raised when the context is missing in Redis."""

    def __init__(self, ctx_id: str) -> None:
        super().__init__(f"Missing context in Redis: {ctx_id}")
        self.ctx_id = ctx_id


class LegoRedisMissingPathError(LegoRedisError):
    """Error raised when the path is missing in Redis."""

    def __init__(self, ctx_id: str, path: str) -> None:
        super().__init__(f"Missing path in Redis Context '{ctx_id}': {path}")
        self.ctx_id = ctx_id
        self.path = path


class LegoRedisTypeError(LegoRedisError):
    """Error raised when the type is wrong in Redis."""

    def __init__(
        self, ctx_id: str, path: str, provided_type: str, expected_type: str
    ) -> None:
        super().__init__(
            f"Wrong type in Redis Context '{ctx_id}': {path}.\n"
            f"Expected type: {expected_type}.\n"
            f"Provided type: {provided_type}."
        )
        self.provided_type = None
        self.expected_type = expected_type
        self.ctx_id = ctx_id
        self.path = path


class RedisBase:
    """Base class for interacting with Redis."""

    def __init__(self, ctx_id: str, connection: RedisConnection) -> None:
        self.redis = redis.Redis(**connection.model_dump())  # type: ignore[attr-defined]
        self.redon = self.redis.json()
        self.ctx_id = ctx_id


class RedisContext(RedisBase):
    """Redis context with get, set, and delete methods."""

    def __init__(
        self,
        ctx_id: str,
        connection: RedisConnection,
        create_parents_on_set: bool = False,
        stricter_key_checking: int = 1,
    ) -> None:
        super().__init__(ctx_id, connection)
        self._create_parents_on_set = create_parents_on_set
        self._stricter_key_checking = stricter_key_checking

    async def init(self) -> None:
        """Initialize the main state."""
        await self.redon.set(self.ctx_id, "$", {}, nx=True)

    async def ctx_ttl(self) -> float | None:
        """Get the time-to-live for the RedisContext."""
        return await self.redis.ttl(self.ctx_id)

    async def set_expiration_time(
        self,
        expires_in: float | None = None,
        init_if_need_be: bool = False,
    ) -> None:
        """
        Set the expiration time for the RedisContext.

        Args:
            :param expires_in: If provided, the expiration time in seconds.
                Will be rounded to the integer by discarding the decimal part.
        """
        if expires_in is not None:
            if expires_in < 0 and expires_in != -1:
                raise ValueError(
                    f"{expires_in=} must be either -1 or a positive number."
                )
        if await self.ctx_ttl() == -2:
            if not init_if_need_be:
                raise ValueError(
                    "Context is not initialized."
                    " Either because expired, deleted, or never initialized."
                )
            await self.init()

        if expires_in is not None and expires_in > 0:
            await self.redis.expire(self.ctx_id, int(expires_in))

    async def get(  # type: ignore[misc]
        self,
        key: str | ReprEnum | None = None,
        fallback_value: Any = None,
        prefix: str | None = None,
        throw_error_if_missing: bool = False,
    ) -> Any:
        """
        Get a key-value pair from the conversation state.

        Args:
            :param key: The key to get the value.
            :param fallback_value: The value to return if the key is not found.
            :param throw_error_if_missing: If True, raise an error
            if the key is not found.
        """
        uri = self._prefix_key(key, prefix)
        result = await self.redon.get(self.ctx_id, uri)
        if throw_error_if_missing and not result:
            raise KeyError(
                f"Missing parent in the {key}"
                f" of the RedisContext: {self.ctx_id}"
            )
        return result[0] if result else fallback_value

    async def verify_key_path(
        self,
        key_path: str,
        create_parents: bool = False,
    ) -> None:
        """
        Check if the key is valid or create a new path.

        Args:
            :param key_path: The key path to check or create.
            :param create_parents: If True, create the parent keys
            if the corresponding dicts do not exist.
        """

        async def check_create_key(uri: str) -> None:
            try:
                value = await self.get(uri, throw_error_if_missing=True)
                if not isinstance(value, dict):
                    raise ValueError(f"Key {uri} is not a dictionary.")
            except KeyError as exc:
                if not create_parents:
                    raise exc

                await self.redon.set(self.ctx_id, uri, {})

        uri = "$"
        for key in str(key_path).split("."):
            if key == "$":
                continue

            if self._stricter_key_checking > 0:
                msg = (
                    (
                        "Key must be a valid identifier."
                        " It must start with a letter or an underscore, and"
                        " can only contain letters, digits, and underscores."
                    )
                    if self._stricter_key_checking == 1
                    else (
                        "Key must have identifier+ format ('+' means dashes"
                        " are allowed as well as the key string can start"
                        " with a digit)"
                    )
                )
                msg += f"\nProvided key: {key}"
                checked_key = (
                    key
                    if self._stricter_key_checking > 1
                    else f"a{key.replace("-", "_")}"
                )
                if not checked_key.isidentifier():
                    raise ValueError(msg)
            await check_create_key(uri)
            uri += f".{key}"

    async def set_(
        self,
        key: str | ReprEnum,
        value: Any,  # type: ignore[misc]
        prefix: str | None = None,
        list_append: bool = False,
        create_parents: bool | None = None,
    ) -> None:
        """
        Set a key-value pair in the conversation state.

        Args:
            :param key: The key to set the value.
            :param value: The value to set.
            :param list_append: If True, the value will be appended to the list
            :param prefix: The prefix to the key.
            :param create_parents: If True, create the parent keys
        """
        if create_parents is None:
            create_parents = self._create_parents_on_set

        uri = self._prefix_key(key, prefix)
        await self.verify_key_path(uri, create_parents=create_parents)

        if list_append:
            potential_list = await self.get(key)
            if potential_list is None:
                await self.redon.set(self.ctx_id, uri, [])
            elif not isinstance(potential_list, list):
                raise ValueError(f"Not a list under the key {key}.")
            await self.redon.arrappend(self.ctx_id, uri, value)
            return

        await self.redon.set(self.ctx_id, uri, value)

    async def count(
        self, key: str | ReprEnum, prefix: str | None = None
    ) -> int:
        """Update the counter under the `key`."""
        if counter := await self.get(key, prefix=prefix):
            if not isinstance(counter, int):
                raise TypeError("Counter is not an integer.")
        else:
            await self.set_(key, 0, prefix=prefix)

        uri = self._prefix_key(key, prefix)
        res = await self.redon.numincrby(self.ctx_id, uri, 1)
        return res[0]

    async def delete(
        self,
        key: str | ReprEnum | None = None,
        prefix: str | None = None,
        throw_error_if_missing: bool = True,
    ) -> Any | None:
        """
        Delete a key-value pair from the conversation state.

        If the key is not found, it will do nothing.
        """
        uri = self._prefix_key(key, prefix)
        value = await self.get(
            uri,
            throw_error_if_missing=throw_error_if_missing,
            fallback_value=_sentinel,
        )
        if value is _sentinel:
            return None

        await self.redon.delete(self.ctx_id, uri)
        return value

    async def close(self) -> None:
        """Close the Redis connection."""
        await self.redis.aclose()

    def _prefix_key(
        self, key: str | ReprEnum | None, prefix: str | None = None
    ) -> str:
        if not prefix and key == "$":
            return "$"

        if prefix and prefix.endswith("."):
            raise ValueError("Malformed prefix: it cannot end with a dot.")

        if not key:
            return prefix or "$"

        key = str(key)
        if not key.isascii():
            raise ValueError(f"Key must be ASCII: {key}")

        if (
            key.startswith(".")
            or key.endswith(".")
            or ".." in key  # this might be reserved by Redis JSON
            or "$.$" in key
        ):
            raise ValueError(
                f"Malformed key: {key}\n"
                "Disallowed patterns in the current implementation: "
                " 'key.' or '.key' or 'double..dot' or '$.$'"
            )
        if key.startswith("$"):
            if prefix or key[1] != ".":
                raise ValueError("Key cannot start with $")

        uri = f"{prefix or '$'}.{key.lstrip('$.')}"
        if not uri.startswith("$"):
            uri = f"$.{uri}"
        return uri


class RedisQueue(RedisBase):
    """Redis queue with get_list, enqueue, and is_full methods."""

    def __init__(
        self,
        ctx_id: str,
        connection: RedisConnection,
        queue_name: str,
        max_size: int,
        max_capacity: int | None = None,
    ) -> None:
        """Initialize the Redis queue.

        Params:
            :param ctx_id: The context ID.
            :param path: The path to the queue.
            :param max_size: The maximum size of the queue
                that can be retrieved with `get_list` method.
            :param max_capacity: The maximum capacity of the queue after
                which the storage is trimmed with `arrtrim` command.
        """
        super().__init__(ctx_id, connection)
        self.max_size = max_size
        self.max_capacity = max_capacity or max_size * 2
        self.queue_name = queue_name
        self._enqueue_script: redis.AsyncScript
        self._is_get_list_likely_working = False

    async def compile_enqueue_script(self) -> None:
        """(Re-)compile the Lua script for enqueueing items."""
        await self._sanity_checks()
        key_path = f"'{self.ctx_id}', '$.{self.queue_name}'"
        self._enqueue_script = self.redis.register_script(
            f"""
            for i = 1, #ARGV do
                redis.call('JSON.ARRAPPEND', {key_path}, ARGV[i])
            end

            --- Get the current length of the array.
            --- Note that JSON.ARRLEN returns an array of results.
            local arr_len_result = redis.call('JSON.ARRLEN', {key_path})
            if arr_len_result and #arr_len_result > 0 then
                local current_length = tonumber(arr_len_result[1])
                if current_length > {self.max_capacity} then
                    local start_index = current_length - {self.max_capacity}
                    local stop_index = current_length - 1
                    redis.call('JSON.ARRTRIM', {key_path}, start_index, stop_index)
                end
            end
            """
        )

    async def enqueue(self, items: list) -> None:
        """Enqueue items to the Redis queue."""
        if not hasattr(self, "_enqueue_script"):
            await self.compile_enqueue_script()
            self._is_get_list_likely_working = True

        await self._enqueue_script(
            keys=[], args=[json.dumps(item) for item in items]
        )

    async def is_full(self) -> bool:
        """Check the number of enqueued items is reached the maximum size."""
        if not self._is_get_list_likely_working:
            await self._sanity_checks()
            self._is_get_list_likely_working = True

        arrlen = await self.redon.arrlen(self.ctx_id, f"$.{self.queue_name}")
        if arrlen and isinstance(arrlen, list) and len(arrlen) > 0:
            current_length = int(arrlen[0])
            return current_length >= self.max_size
        return False

    async def get_list(self) -> list:
        """
        Retrieve the queue as a Python list.

        Returns the last `self.max_size` elements.
        """
        if not self._is_get_list_likely_working:
            await self._sanity_checks()
            self._is_get_list_likely_working = True

        slice_path = f"{self.queue_name}[-{self.max_size}:]"
        return await self.redon.get(self.ctx_id, f"$.{slice_path}")

    async def _sanity_checks(self) -> None:
        """Perform sanity checks on the queue."""
        if not await self.redis.exists(self.ctx_id):
            raise LegoRedisMissingContextError(self.ctx_id)

        type_ = await self.redon.type(self.ctx_id, f"$.{self.queue_name}")
        if not type:
            await self.redon.set(self.ctx_id, "$", {})
            await self.redon.set(self.ctx_id, f"$.{self.queue_name}", [])
        elif type_[0] != b"array":
            raise LegoRedisTypeError(
                self.ctx_id, f"$.{self.queue_name}", type_[0], "array"
            )
