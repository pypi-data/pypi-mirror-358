import asyncio
import logging
from typing import Any, Callable, Iterable, Optional, Tuple, Union, get_args, get_origin

import aiohttp

from .headers import Authorization, Header
from .method import Method
from .objects import RequestData, Response

logger = logging.getLogger("api-lib")


class ApiLib:
    headers: list[Header] = []

    def __init__(
        self,
        url: str,
        token: Authorization,
        prefix: Optional[str] = None,
    ):
        self.host = url
        self.token = token
        self.prefix = prefix or ""
        self._headers = {k: v for h in (self.headers or []) for k, v in h.header.items()}

    async def __call(
        self,
        method: Method,
        path: str,
        data: Optional[RequestData] = None,
        use_api_prefix: bool = True,
    ):
        logger.debug(
            "Hitting API",
            {
                "host": self.host,
                "method": method.value,
                "path": path,
                "data": getattr(data, "as_dict", {}),
            },
        )
        try:
            async with aiohttp.ClientSession(headers=self.token.header) as s:
                async with getattr(s, method.value)(
                    url=f"{self.host}{self.prefix if use_api_prefix else ''}{path}",
                    json={} if data is None else data.as_dict,
                    headers=self._headers,
                ) as res:
                    try:
                        data = await res.json()
                    except Exception:
                        data = await res.text()

                    return (res.status // 200) == 1, data
        except OSError as err:
            logger.error(
                "OSError while doing an API call",
                {
                    "error": str(err),
                    "host": self.host,
                    "method": method.value,
                    "path": path,
                },
            )

        except Exception as err:
            logger.error(
                f"Exception while doing an API call {err}",
                {
                    "error": str(err),
                    "host": self.host,
                    "method": method.value,
                    "path": path,
                },
            )

        return (False, None)

    async def __call_api_with_timeout(
        self,
        method: Method,
        path: str,
        data: Optional[RequestData] = None,
        timeout: int = 90,
        use_api_prefix: bool = True,
    ) -> tuple[bool, Optional[object]]:
        backoff = 0.5
        while True:
            try:
                result = await asyncio.wait_for(
                    asyncio.create_task(self.__call(method, path, data, use_api_prefix)),
                    timeout=timeout,
                )
            except aiohttp.ClientConnectionError as err:
                backoff *= 2
                logger.exception(
                    "ClientConnection exception while doing an API call.",
                    {
                        "error": str(err),
                        "host": self.host,
                        "method": method.value,
                        "path": path,
                        "backoff": backoff,
                    },
                )
                if backoff > 10:
                    return (False, None)
                await asyncio.sleep(backoff)

            except asyncio.TimeoutError as err:
                logger.error(
                    "Timeout error while doing an API call",
                    {
                        "error": str(err),
                        "host": self.host,
                        "method": method.value,
                        "path": path,
                    },
                )
                return (False, None)
            else:
                return result

    async def try_req(
        self,
        method: Method,
        path: str,
        resp_type: Optional[Callable] = None,
        data: Optional[RequestData] = None,
        use_api_prefix: bool = True,
        return_state: bool = False,
        timeout: int = 90,
    ) -> Optional[Union[Response, dict]]:
        is_ok, r = await self.__call_api_with_timeout(
            method, path, data, timeout=timeout, use_api_prefix=use_api_prefix
        )

        if return_state:
            return is_ok

        if not is_ok:
            return None

        if resp_type is None:
            return r

        origin: Optional[Any] = get_origin(resp_type)
        args: Tuple[Optional[Any], ...] = get_args(resp_type)

        if origin and issubclass(origin, Iterable) and args:
            return [args[0](item) for item in r]
        else:
            return resp_type(r)  # ty: ignore[call-non-callable]

    async def req(
        self,
        method: Method,
        path: str,
        resp_type: Optional[Callable] = None,
        data: Optional[RequestData] = None,
        use_api_prefix: bool = True,
        return_state: bool = False,
        timeout: int = 90,
    ) -> Union[Response]:
        resp = await self.try_req(
            method,
            path,
            resp_type,
            data,
            use_api_prefix,
            return_state,
            timeout,
        )

        if resp is None:
            logger.error(
                "API request failed",
                {
                    "method": method.value,
                    "path": path,
                    "data": getattr(data, "as_dict", {}),
                },
            )
            raise RuntimeError("API request failed")
        return resp

    async def timeout_check_success(self, path: str, timeout: int = 20):
        try:
            is_ok = await asyncio.wait_for(self.__check_url(path), timeout=timeout)
        except (asyncio.TimeoutError, Exception):
            return False
        else:
            return is_ok

    async def __check_url(self, path: str, use_api_prefix: bool = False):
        is_ok = False
        while not is_ok:
            try:
                is_ok = await self.req(
                    Method.GET,
                    path,
                    use_api_prefix=use_api_prefix,
                    return_state=True,
                    timeout=None,
                )
            except Exception:
                await asyncio.sleep(0.25)
            else:
                if is_ok:
                    return is_ok
