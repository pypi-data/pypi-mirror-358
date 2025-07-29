from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cc_connection_approved_country_response_dto import CCConnectionApprovedCountryResponseDto
from ...types import UNSET, Response


def _get_kwargs(
    connection_id: str,
    id: str,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["tenantId"] = tenant_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/v1/cloud/connections/{connection_id}/approved-countries/{id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[CCConnectionApprovedCountryResponseDto]:
    if response.status_code == 200:
        response_200 = CCConnectionApprovedCountryResponseDto.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[CCConnectionApprovedCountryResponseDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    connection_id: str,
    id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Response[CCConnectionApprovedCountryResponseDto]:
    """Remove approved country

     Remove a country for a given connection by its ID.

    Args:
        connection_id (str):
        id (str):
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CCConnectionApprovedCountryResponseDto]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
        id=id,
        tenant_id=tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    connection_id: str,
    id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Optional[CCConnectionApprovedCountryResponseDto]:
    """Remove approved country

     Remove a country for a given connection by its ID.

    Args:
        connection_id (str):
        id (str):
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CCConnectionApprovedCountryResponseDto
    """

    return sync_detailed(
        connection_id=connection_id,
        id=id,
        client=client,
        tenant_id=tenant_id,
    ).parsed


async def asyncio_detailed(
    connection_id: str,
    id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Response[CCConnectionApprovedCountryResponseDto]:
    """Remove approved country

     Remove a country for a given connection by its ID.

    Args:
        connection_id (str):
        id (str):
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CCConnectionApprovedCountryResponseDto]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
        id=id,
        tenant_id=tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    connection_id: str,
    id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Optional[CCConnectionApprovedCountryResponseDto]:
    """Remove approved country

     Remove a country for a given connection by its ID.

    Args:
        connection_id (str):
        id (str):
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CCConnectionApprovedCountryResponseDto
    """

    return (
        await asyncio_detailed(
            connection_id=connection_id,
            id=id,
            client=client,
            tenant_id=tenant_id,
        )
    ).parsed
