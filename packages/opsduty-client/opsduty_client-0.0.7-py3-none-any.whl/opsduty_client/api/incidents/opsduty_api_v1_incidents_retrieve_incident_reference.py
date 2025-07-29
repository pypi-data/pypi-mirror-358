from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.incident_reference_schema import IncidentReferenceSchema
from ...types import Response


def _get_kwargs(
    incident_reference_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/incidents/incident-reference/{incident_reference_id}/".format(
            incident_reference_id=incident_reference_id,
        ),
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[IncidentReferenceSchema]:
    if response.status_code == 200:
        response_200 = IncidentReferenceSchema.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[IncidentReferenceSchema]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    incident_reference_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[IncidentReferenceSchema]:
    """Retrieve Incident Reference

    Args:
        incident_reference_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[IncidentReferenceSchema]
    """

    kwargs = _get_kwargs(
        incident_reference_id=incident_reference_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    incident_reference_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[IncidentReferenceSchema]:
    """Retrieve Incident Reference

    Args:
        incident_reference_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        IncidentReferenceSchema
    """

    return sync_detailed(
        incident_reference_id=incident_reference_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    incident_reference_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[IncidentReferenceSchema]:
    """Retrieve Incident Reference

    Args:
        incident_reference_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[IncidentReferenceSchema]
    """

    kwargs = _get_kwargs(
        incident_reference_id=incident_reference_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    incident_reference_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[IncidentReferenceSchema]:
    """Retrieve Incident Reference

    Args:
        incident_reference_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        IncidentReferenceSchema
    """

    return (
        await asyncio_detailed(
            incident_reference_id=incident_reference_id,
            client=client,
        )
    ).parsed
