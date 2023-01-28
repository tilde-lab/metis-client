"""Low level http and SSE client"""

from asyncio import CancelledError, TimeoutError as AsyncioTimeoutError, sleep
from concurrent.futures import TimeoutError as FuturesTimeoutError
from contextlib import suppress
from datetime import timedelta
from functools import partial
from typing import Any, Callable, Dict, Mapping, Optional, Union

import aiohttp
from aiohttp import ClientResponse, ClientTimeout
from aiohttp.client import _RequestContextManager
from aiohttp.client_exceptions import (
    ClientConnectionError,
    ClientPayloadError,
    InvalidURL,
)
from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPInternalServerError,
    HTTPMisdirectedRequest,
    HTTPNotFound,
    HTTPPaymentRequired,
    HTTPTooManyRequests,
    HTTPUnauthorized,
)
from aiohttp_sse_client import client as sse_client
from yarl import URL

from .auth import BaseAuthenticator, MetisNoAuth
from .const import HttpContentType, HttpMethods
from .exc import (
    MetisAuthenticationException,
    MetisConnectionException,
    MetisException,
    MetisHttpResponseError,
    MetisNotFoundException,
    MetisPayloadException,
    MetisQuotaException,
)
from .models.base import MetisBase


class MetisClient(MetisBase):
    """
    Client to handle API calls.
    Don't use this directly, use `metis_client.metis.Metis` to get the client.
    """

    _auth: BaseAuthenticator
    _base_url: URL

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: URL,
        auth: Optional[BaseAuthenticator] = None,
    ) -> None:
        """
        Initialize the Metis API client.
        **Arguments:**
        `session`: The aiohttp client session to use for making requests.
        `base_url`: Root URL in form of `yarl.URL`.
        `auth`: Authenticator, subclass of `BaseAuthenticator`.
        """
        self._session = session
        self._auth = auth or MetisNoAuth()
        self._base_url = base_url

    async def _do_auth(self, force: bool = False) -> None:
        async with self._auth.lock:
            if force or await self._auth.should_update(self._session, self._base_url):
                await self._auth.authenticate(self._session, self._base_url)

    @staticmethod
    def _response_raise_for_status(result: ClientResponse, body: Any) -> None:
        if result.ok:
            return
        status = result.status
        msg = f"Response exception for {str(result.url)!r} with code {status}: {body}"
        proto_err = MetisHttpResponseError
        if status in (HTTPForbidden.status_code, HTTPUnauthorized.status_code):
            proto_err = MetisAuthenticationException
        if status == HTTPNotFound.status_code:
            proto_err = MetisNotFoundException
        if status == HTTPBadRequest.status_code:
            proto_err = MetisPayloadException
        if status == HTTPPaymentRequired.status_code:
            proto_err = MetisQuotaException
        if status == HTTPMisdirectedRequest.status_code:
            proto_err = MetisHttpResponseError
        fallback_msg = "Error message is not provided"
        raise proto_err(
            result.request_info,
            history=(result,),
            message=msg,
            status=result.status,
            error=body.get("error", fallback_msg)
            if isinstance(body, dict)
            else str(body or fallback_msg),
        )

    # pylint: disable=too-many-arguments
    async def _request(
        self,
        url: URL,
        json: Optional[Any] = None,
        data: Union[str, bytes, None] = None,
        headers: Optional[Mapping[str, Any]] = None,
        method: HttpMethods = "GET",
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        auth_required: bool = False,
        **_,
    ) -> ClientResponse:
        """
        Makes an HTTP request to the specified endpoint using the specified parameters.
        """
        do_req = partial(
            self._session.request,
            method,
            url,
            params=params,
            timeout=timeout,
            headers=headers,
            json=json,
            data=data,
            raise_for_status=False,
        )

        # preauthenticate
        if auth_required:
            await self._do_auth()

        try:
            result = await do_req()

            # redo if failed because of auth
            if result.status == HTTPUnauthorized.status_code:
                # forced auth for first request
                # normal auth (only if needed) for all other
                await self._do_auth(force=not self._auth.lock.locked())
                result.close()
                result = await do_req()
            # rate limit - redo all
            if result.status == HTTPTooManyRequests.status_code:
                await sleep(10)
                result.close()
                return await self._request(
                    url, json, data, headers, method, params, timeout, auth_required
                )

        except (
            CancelledError,
            ClientConnectionError,
            ClientPayloadError,
            InvalidURL,
        ) as exc:
            raise MetisConnectionException(
                f"Request exception for {str(url)!r} with - {exc}"
            ) from exc

        except (TimeoutError, AsyncioTimeoutError, FuturesTimeoutError):
            raise MetisConnectionException(
                f"Timeout of {timeout} reached while waiting for {str(url)}"
            ) from None

        except BaseException as exc:
            raise MetisException(
                f"Unexpected exception for {str(url)!r} with - {exc}"
            ) from exc

        try:
            body = None
            if result.content_type in (HttpContentType.BASE_JSON, HttpContentType):
                body = await result.json(
                    encoding="utf-8", content_type=result.content_type
                )
            elif result.content_type in (
                HttpContentType.TEXT_HTML,
                HttpContentType.TEXT_PLAIN,
            ):
                body = await result.text("utf-8")
                body = body[:100]
            else:
                body = await result.read()
                body = body[:100]
        except BaseException as exc:
            raise MetisException(
                f"Could not handle response data from {str(url)!r} with - {exc}"
            ) from exc

        self._response_raise_for_status(result, body)

        return result

    # pylint: disable=too-many-arguments
    def request(
        self,
        url: URL,
        json: Optional[Any] = None,
        data: Union[str, bytes, None] = None,
        headers: Optional[Mapping[str, Any]] = None,
        method: HttpMethods = "GET",
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        auth_required: bool = False,
        **_,
    ) -> _RequestContextManager:
        """
        Makes an HTTP request to the specified endpoint using the specified parameters.
        This method is asynchronous, meaning that it will not block the execution
        of the program while the request is being made and processed.
        **Arguments**:
        -  `url` (Required): The API endpoint to call.
        **Optional arguments**:
        - `data`: The data to include in the request body. Can be a dictionary,
           a string, or None.
        - `headers`: The headers to include in the request. Can be a dictionary or None.
        - `method`: The HTTP method to use for the request. Defaults to GET.
        - `params`: The query parameters to include in the request.
           Can be a dictionary or None.
        - `timeout`: The maximum amount of time to wait for the request to complete,
          in seconds. Can be an integer or None.
        - `auth_required`: Flag that auth requered for this request
        Returns:
        A `aiohttp.client._RequestContextManager` object representing the API response
        """
        return _RequestContextManager(
            self._request(
                url, json, data, headers, method, params, timeout, auth_required
            )
        )

    def _parse_sse_error(self, error: str) -> Optional[int]:
        """
        Helper function to parse the error code from a SSE exception
        Error message format is 'fetch {} failed: {}'.format(url, status)
        """
        with suppress(ValueError):
            return int(error.split(": ")[-1])

    async def sse(
        self,
        url: URL,
        on_message: Callable[[sse_client.MessageEvent], None],
        on_open: Callable[[], None],
        params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Creates `aiohttp_sse_client.client.EventSource` object with sensible defaults.
        **Arguments**:
        -  `url` (Required): The API endpoint to connect.
        -  `on_message` (Required): Message callback
        -  `on_open` (Required): Callback when connected
        **Optional arguments**:
        - `params`: The query parameters to include in the request.
           Can be a dictionary or None.
        Returns: None
        """
        original_backoff = 0.1
        backoff = original_backoff

        timeout = ClientTimeout(total=None, sock_connect=600, sock_read=None)
        while True:
            try:
                await self._do_auth()
                async with sse_client.EventSource(
                    str(url),
                    reconnection_time=timedelta(seconds=original_backoff),
                    on_open=on_open,
                    session=self._session,
                    params=params,
                    timeout=timeout,
                    read_bufsize=2**19,
                    raise_for_status=False,
                ) as evt_src:
                    backoff = original_backoff
                    async for evt in evt_src:
                        on_message(evt)

            except CancelledError:
                # task is cancelled - abort
                break

            except ClientConnectionError as err:
                backoff *= 2
                self.logger.warning(
                    "%s connection error %s - reconnecting in %s seconds",
                    self._base_url,
                    err,
                    backoff,
                )
                await sleep(backoff)
                continue

            except ConnectionRefusedError as err:
                status = self._parse_sse_error(err.args[0])
                if status == HTTPUnauthorized.status_code:
                    self.logger.info(
                        "%s - authentication requered - reconnecting after reauth",
                        self._base_url,
                    )
                    await self._do_auth(force=True)
                    continue
                raise

            except ConnectionAbortedError as err:
                self.logger.error("%s connection error %s - abort", self._base_url, err)
                break

            except ConnectionError as err:
                status = self._parse_sse_error(err.args[0])
                if status and (
                    status == HTTPTooManyRequests.status_code
                    or status >= HTTPInternalServerError.status_code
                ):
                    backoff *= 2
                    self.logger.warning(
                        "%s connection error %s - reconnecting in %s seconds",
                        self._base_url,
                        err,
                        backoff,
                    )
                    continue
                self.logger.error("%s connection error %s - abort", self._base_url, err)
                break

            except (TimeoutError, AsyncioTimeoutError, FuturesTimeoutError):
                self.logger.warning(
                    "%s endpoint timeouted - reconnecting", self._base_url
                )
                continue

            except ClientPayloadError:
                self.logger.warning(
                    "%s endpoint malformed response - reconnecting", self._base_url
                )
                continue
