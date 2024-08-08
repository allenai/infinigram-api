import os
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI, Request
from pyinstrument import Profiler
from pyinstrument.renderers.html import HTMLRenderer
from pyinstrument.renderers.speedscope import SpeedscopeRenderer

from src.config import get_config

current_dir = Path(os.getcwd())
performance_profiles_directory = current_dir / "performance-profiles"


def register_profiling_middleware(app: FastAPI) -> Any:
    config = get_config()

    if config.profiling_enabled is True:

        @app.middleware("http")
        async def profile_request(request: Request, call_next: Callable[..., Any]):  # type: ignore
            """Profile the current request

            Taken from https://blog.balthazar-rouberol.com/how-to-profile-a-fastapi-asynchronous-request and https://github.com/brouberol/5esheets/blob/main/dnd5esheets/middlewares.py#L134

            """

            profile_type_to_ext = {"html": "html", "speedscope": "speedscope.json"}
            profile_type_to_renderer = {
                "html": HTMLRenderer,
                "speedscope": SpeedscopeRenderer,
            }

            if request.query_params.get("profile", False):
                profile_type = request.query_params.get("profile_format", "speedscope")
                with Profiler(interval=0.001, async_mode="enabled") as profiler:
                    response = await call_next(request)
                extension = profile_type_to_ext[profile_type]
                renderer = profile_type_to_renderer[profile_type]()

                os.makedirs(performance_profiles_directory, exist_ok=True)

                with open(
                    current_dir / f"performance-profiles/profile.{extension}", "w"
                ) as out:
                    out.write(profiler.output(renderer=renderer))

                return response

            return await call_next(request)
