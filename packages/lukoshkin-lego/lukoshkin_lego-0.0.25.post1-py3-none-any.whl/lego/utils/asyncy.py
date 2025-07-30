import asyncio
from typing import Awaitable, TypeVar

T = TypeVar("T")


async def gather_with_upper_bound(
    max_concurrency: int, *coros: Awaitable[T]
) -> list[T]:
    """Gather coroutines with an upper bound on concurrency."""
    semaphore = asyncio.Semaphore(max_concurrency)

    async def sem_coro(coro: Awaitable[T]) -> T:
        async with semaphore:
            return await coro

    return await asyncio.gather(*(sem_coro(c) for c in coros))
