from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.heartbeat_schema import HeartbeatSchema
from ...models.update_heartbeat_input import UpdateHeartbeatInput
from ...types import Response


def _get_kwargs(
    heartbeat_id: int,
    *,
    body: UpdateHeartbeatInput,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v1/heartbeats/{heartbeat_id}/".format(
            heartbeat_id=heartbeat_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[HeartbeatSchema]:
    if response.status_code == 200:
        response_200 = HeartbeatSchema.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[HeartbeatSchema]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    heartbeat_id: int,
    *,
    client: AuthenticatedClient,
    body: UpdateHeartbeatInput,
) -> Response[HeartbeatSchema]:
    """Update Heartbeat

    Args:
        heartbeat_id (int):
        body (UpdateHeartbeatInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HeartbeatSchema]
    """

    kwargs = _get_kwargs(
        heartbeat_id=heartbeat_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    heartbeat_id: int,
    *,
    client: AuthenticatedClient,
    body: UpdateHeartbeatInput,
) -> Optional[HeartbeatSchema]:
    """Update Heartbeat

    Args:
        heartbeat_id (int):
        body (UpdateHeartbeatInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HeartbeatSchema
    """

    return sync_detailed(
        heartbeat_id=heartbeat_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    heartbeat_id: int,
    *,
    client: AuthenticatedClient,
    body: UpdateHeartbeatInput,
) -> Response[HeartbeatSchema]:
    """Update Heartbeat

    Args:
        heartbeat_id (int):
        body (UpdateHeartbeatInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HeartbeatSchema]
    """

    kwargs = _get_kwargs(
        heartbeat_id=heartbeat_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    heartbeat_id: int,
    *,
    client: AuthenticatedClient,
    body: UpdateHeartbeatInput,
) -> Optional[HeartbeatSchema]:
    """Update Heartbeat

    Args:
        heartbeat_id (int):
        body (UpdateHeartbeatInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HeartbeatSchema
    """

    return (
        await asyncio_detailed(
            heartbeat_id=heartbeat_id,
            client=client,
            body=body,
        )
    ).parsed
