from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import Response


def _get_kwargs(
    service_id: int,
    name: str,
    environment: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/heartbeats/checkin/{service_id}/{name}/{environment}".format(
            service_id=service_id,
            name=name,
            environment=environment,
        ),
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == 200:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    service_id: int,
    name: str,
    environment: str,
    *,
    client: AuthenticatedClient,
) -> Response[Any]:
    """Healthcheck Environment Checkin

     API to register an healthcheck checkin.

    This is different from the public apis, we can lookuo by name and environment
    if the user is authenticated.

    Args:
        service_id (int):
        name (str):
        environment (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        name=name,
        environment=environment,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    service_id: int,
    name: str,
    environment: str,
    *,
    client: AuthenticatedClient,
) -> Response[Any]:
    """Healthcheck Environment Checkin

     API to register an healthcheck checkin.

    This is different from the public apis, we can lookuo by name and environment
    if the user is authenticated.

    Args:
        service_id (int):
        name (str):
        environment (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        name=name,
        environment=environment,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
