from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cc_paginated_connection_users_approved_countries_response_dto import (
    CCPaginatedConnectionUsersApprovedCountriesResponseDto,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    connection_id: str,
    connection_user_id: str,
    *,
    tenant_id: str,
    take: Union[Unset, float] = 100.0,
    skip: Union[Unset, float] = 0.0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["tenantId"] = tenant_id

    params["take"] = take

    params["skip"] = skip

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/cloud/connections/{connection_id}/users/{connection_user_id}/approved-countries",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[CCPaginatedConnectionUsersApprovedCountriesResponseDto]:
    if response.status_code == 200:
        response_200 = CCPaginatedConnectionUsersApprovedCountriesResponseDto.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[CCPaginatedConnectionUsersApprovedCountriesResponseDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    connection_id: str,
    connection_user_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
    take: Union[Unset, float] = 100.0,
    skip: Union[Unset, float] = 0.0,
) -> Response[CCPaginatedConnectionUsersApprovedCountriesResponseDto]:
    """List approved countries for user

     List approved countries

    Args:
        connection_id (str):
        connection_user_id (str):
        tenant_id (str):
        take (Union[Unset, float]):  Default: 100.0.
        skip (Union[Unset, float]):  Default: 0.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CCPaginatedConnectionUsersApprovedCountriesResponseDto]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
        connection_user_id=connection_user_id,
        tenant_id=tenant_id,
        take=take,
        skip=skip,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    connection_id: str,
    connection_user_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
    take: Union[Unset, float] = 100.0,
    skip: Union[Unset, float] = 0.0,
) -> Optional[CCPaginatedConnectionUsersApprovedCountriesResponseDto]:
    """List approved countries for user

     List approved countries

    Args:
        connection_id (str):
        connection_user_id (str):
        tenant_id (str):
        take (Union[Unset, float]):  Default: 100.0.
        skip (Union[Unset, float]):  Default: 0.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CCPaginatedConnectionUsersApprovedCountriesResponseDto
    """

    return sync_detailed(
        connection_id=connection_id,
        connection_user_id=connection_user_id,
        client=client,
        tenant_id=tenant_id,
        take=take,
        skip=skip,
    ).parsed


async def asyncio_detailed(
    connection_id: str,
    connection_user_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
    take: Union[Unset, float] = 100.0,
    skip: Union[Unset, float] = 0.0,
) -> Response[CCPaginatedConnectionUsersApprovedCountriesResponseDto]:
    """List approved countries for user

     List approved countries

    Args:
        connection_id (str):
        connection_user_id (str):
        tenant_id (str):
        take (Union[Unset, float]):  Default: 100.0.
        skip (Union[Unset, float]):  Default: 0.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CCPaginatedConnectionUsersApprovedCountriesResponseDto]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
        connection_user_id=connection_user_id,
        tenant_id=tenant_id,
        take=take,
        skip=skip,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    connection_id: str,
    connection_user_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
    take: Union[Unset, float] = 100.0,
    skip: Union[Unset, float] = 0.0,
) -> Optional[CCPaginatedConnectionUsersApprovedCountriesResponseDto]:
    """List approved countries for user

     List approved countries

    Args:
        connection_id (str):
        connection_user_id (str):
        tenant_id (str):
        take (Union[Unset, float]):  Default: 100.0.
        skip (Union[Unset, float]):  Default: 0.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CCPaginatedConnectionUsersApprovedCountriesResponseDto
    """

    return (
        await asyncio_detailed(
            connection_id=connection_id,
            connection_user_id=connection_user_id,
            client=client,
            tenant_id=tenant_id,
            take=take,
            skip=skip,
        )
    ).parsed
