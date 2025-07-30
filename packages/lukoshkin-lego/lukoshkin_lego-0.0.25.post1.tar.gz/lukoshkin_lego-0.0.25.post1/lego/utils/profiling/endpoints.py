"""Profiling endpoints."""

from pathlib import Path
from typing import Callable
from uuid import uuid4

from fastapi import Request
from pyinstrument import Profiler

from lego.lego_types import ProfilerSessions
from lego.logger import logger
from lego.rag.container import container
from lego.utils.profiling.base import WallClock


async def profile_endpoints(request: Request, call_next: Callable):
    """Profile endpoints that requested to do so."""
    if request.query_params.get("profile", "no") == "no":
        return await call_next(request)

    if request.query_params["profile"] == "pyinstrument":
        with Profiler(async_mode="enabled") as profiler:
            response = await call_next(request)

        if save_at := request.query_params.get("save_profile_at"):
            save_at = Path(save_at).resolve()
            if save_at.exists():
                raise FileExistsError(f"Path already exists: {save_at}")

            save_at.parent.mkdir(parents=True, exist_ok=True)
            profiler.write_html(save_at.with_suffix(".html"))
            logger.info(f"Saved profiling results to {save_at}")

        logger.info(f"Profiling results of {request.url.path}:")
        logger.info(profiler.output_text(unicode=True, color=True))
        return response

    if request.query_params["profile"] != "custom":
        raise ValueError("Invalid 'profile' value")

    with WallClock() as wc:
        response = await call_next(request)

    sessions = container.resolve(ProfilerSessions)
    sessions[request.url.path][uuid4().hex] = wc.wall_time()
    return response
