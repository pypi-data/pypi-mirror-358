from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cron_heartbeat_state_schema import CronHeartbeatStateSchema
from ...models.interval_heartbeat_state_schema import IntervalHeartbeatStateSchema
from ...models.update_heartbeat_state_input import UpdateHeartbeatStateInput
from ...types import Response


def _get_kwargs(
    heartbeat_state_id: int,
    *,
    body: UpdateHeartbeatStateInput,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v1/heartbeats/states/{heartbeat_state_id}/".format(
            heartbeat_state_id=heartbeat_state_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union["CronHeartbeatStateSchema", "IntervalHeartbeatStateSchema"]]:
    if response.status_code == 200:

        def _parse_response_200(data: object) -> Union["CronHeartbeatStateSchema", "IntervalHeartbeatStateSchema"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200_type_0 = CronHeartbeatStateSchema.from_dict(data)

                return response_200_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_200_type_1 = IntervalHeartbeatStateSchema.from_dict(data)

            return response_200_type_1

        response_200 = _parse_response_200(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union["CronHeartbeatStateSchema", "IntervalHeartbeatStateSchema"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    heartbeat_state_id: int,
    *,
    client: AuthenticatedClient,
    body: UpdateHeartbeatStateInput,
) -> Response[Union["CronHeartbeatStateSchema", "IntervalHeartbeatStateSchema"]]:
    """Update Heartbeat State

    Args:
        heartbeat_state_id (int):
        body (UpdateHeartbeatStateInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union['CronHeartbeatStateSchema', 'IntervalHeartbeatStateSchema']]
    """

    kwargs = _get_kwargs(
        heartbeat_state_id=heartbeat_state_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    heartbeat_state_id: int,
    *,
    client: AuthenticatedClient,
    body: UpdateHeartbeatStateInput,
) -> Optional[Union["CronHeartbeatStateSchema", "IntervalHeartbeatStateSchema"]]:
    """Update Heartbeat State

    Args:
        heartbeat_state_id (int):
        body (UpdateHeartbeatStateInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union['CronHeartbeatStateSchema', 'IntervalHeartbeatStateSchema']
    """

    return sync_detailed(
        heartbeat_state_id=heartbeat_state_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    heartbeat_state_id: int,
    *,
    client: AuthenticatedClient,
    body: UpdateHeartbeatStateInput,
) -> Response[Union["CronHeartbeatStateSchema", "IntervalHeartbeatStateSchema"]]:
    """Update Heartbeat State

    Args:
        heartbeat_state_id (int):
        body (UpdateHeartbeatStateInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union['CronHeartbeatStateSchema', 'IntervalHeartbeatStateSchema']]
    """

    kwargs = _get_kwargs(
        heartbeat_state_id=heartbeat_state_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    heartbeat_state_id: int,
    *,
    client: AuthenticatedClient,
    body: UpdateHeartbeatStateInput,
) -> Optional[Union["CronHeartbeatStateSchema", "IntervalHeartbeatStateSchema"]]:
    """Update Heartbeat State

    Args:
        heartbeat_state_id (int):
        body (UpdateHeartbeatStateInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union['CronHeartbeatStateSchema', 'IntervalHeartbeatStateSchema']
    """

    return (
        await asyncio_detailed(
            heartbeat_state_id=heartbeat_state_id,
            client=client,
            body=body,
        )
    ).parsed
