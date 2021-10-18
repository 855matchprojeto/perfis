import uuid
from typing import Any, Optional, Union
from starlette.requests import HTTPConnection, Request
from starlette_context.plugins import Plugin


class RequestPlugin(Plugin):

    key = "request"

    async def process_request(
        self, request: Union[Request, HTTPConnection]
    ) -> Optional[Any]:
        return {
            "request": request,
        }

