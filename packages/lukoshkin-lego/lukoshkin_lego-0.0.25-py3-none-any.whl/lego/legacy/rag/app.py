"""Swagger for ingest and retrieve routers."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from lego.rag.api_routers import ingest, misc, retrieve
from lego.rag.container import container
from lego.rag.container_types import UseProfiler
from lego.utils.profiling import profile_endpoints

URL_PREFIX = "/rag"
app = FastAPI(
    openapi_url=f"{URL_PREFIX}/openapi.json",
    docs_url=f"{URL_PREFIX}/docs",
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (e.g., GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
if container.resolve(UseProfiler):

    @app.middleware("httpx")
    def profiling_middleware(request: Request, call_next):
        """Allow endpoints to request to profile."""
        return profile_endpoints(request, call_next)


app.include_router(ingest.router, prefix=URL_PREFIX)
app.include_router(retrieve.router, prefix=URL_PREFIX)
app.include_router(misc.router, prefix=URL_PREFIX)


if __name__ == "__main__":
    import uvicorn  # noqa: WPS433 (nested import)

    uvicorn.run("app:app", host="127.0.0.1", port=3000, reload=True)
