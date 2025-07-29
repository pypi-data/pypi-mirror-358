from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cc_paginated_connection_users_response_dto import CCPaginatedConnectionUsersResponseDto
from ...models.get_list_users_order_by import GetListUsersOrderBy
from ...models.get_list_users_sort_direction import GetListUsersSortDirection
from ...types import UNSET, Response, Unset


def _get_kwargs(
    connection_id: str,
    *,
    tenant_id: str,
    take: Union[Unset, float] = 100.0,
    skip: Union[Unset, float] = 0.0,
    sort_direction: Union[Unset, GetListUsersSortDirection] = "ASC",
    order_by: Union[Unset, GetListUsersOrderBy] = "name",
    search: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["tenantId"] = tenant_id

    params["take"] = take

    params["skip"] = skip

    json_sort_direction: Union[Unset, str] = UNSET
    if not isinstance(sort_direction, Unset):
        json_sort_direction = sort_direction

    params["sortDirection"] = json_sort_direction

    json_order_by: Union[Unset, str] = UNSET
    if not isinstance(order_by, Unset):
        json_order_by = order_by

    params["orderBy"] = json_order_by

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/cloud/connections/{connection_id}/users",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[CCPaginatedConnectionUsersResponseDto]:
    if response.status_code == 200:
        response_200 = CCPaginatedConnectionUsersResponseDto.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[CCPaginatedConnectionUsersResponseDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    connection_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
    take: Union[Unset, float] = 100.0,
    skip: Union[Unset, float] = 0.0,
    sort_direction: Union[Unset, GetListUsersSortDirection] = "ASC",
    order_by: Union[Unset, GetListUsersOrderBy] = "name",
    search: Union[Unset, str] = UNSET,
) -> Response[CCPaginatedConnectionUsersResponseDto]:
    """List users

     Get users for connection

    Args:
        connection_id (str):
        tenant_id (str):
        take (Union[Unset, float]):  Default: 100.0.
        skip (Union[Unset, float]):  Default: 0.0.
        sort_direction (Union[Unset, GetListUsersSortDirection]):  Default: 'ASC'.
        order_by (Union[Unset, GetListUsersOrderBy]):  Default: 'name'.
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CCPaginatedConnectionUsersResponseDto]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
        tenant_id=tenant_id,
        take=take,
        skip=skip,
        sort_direction=sort_direction,
        order_by=order_by,
        search=search,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    connection_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
    take: Union[Unset, float] = 100.0,
    skip: Union[Unset, float] = 0.0,
    sort_direction: Union[Unset, GetListUsersSortDirection] = "ASC",
    order_by: Union[Unset, GetListUsersOrderBy] = "name",
    search: Union[Unset, str] = UNSET,
) -> Optional[CCPaginatedConnectionUsersResponseDto]:
    """List users

     Get users for connection

    Args:
        connection_id (str):
        tenant_id (str):
        take (Union[Unset, float]):  Default: 100.0.
        skip (Union[Unset, float]):  Default: 0.0.
        sort_direction (Union[Unset, GetListUsersSortDirection]):  Default: 'ASC'.
        order_by (Union[Unset, GetListUsersOrderBy]):  Default: 'name'.
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CCPaginatedConnectionUsersResponseDto
    """

    return sync_detailed(
        connection_id=connection_id,
        client=client,
        tenant_id=tenant_id,
        take=take,
        skip=skip,
        sort_direction=sort_direction,
        order_by=order_by,
        search=search,
    ).parsed


async def asyncio_detailed(
    connection_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
    take: Union[Unset, float] = 100.0,
    skip: Union[Unset, float] = 0.0,
    sort_direction: Union[Unset, GetListUsersSortDirection] = "ASC",
    order_by: Union[Unset, GetListUsersOrderBy] = "name",
    search: Union[Unset, str] = UNSET,
) -> Response[CCPaginatedConnectionUsersResponseDto]:
    """List users

     Get users for connection

    Args:
        connection_id (str):
        tenant_id (str):
        take (Union[Unset, float]):  Default: 100.0.
        skip (Union[Unset, float]):  Default: 0.0.
        sort_direction (Union[Unset, GetListUsersSortDirection]):  Default: 'ASC'.
        order_by (Union[Unset, GetListUsersOrderBy]):  Default: 'name'.
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CCPaginatedConnectionUsersResponseDto]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
        tenant_id=tenant_id,
        take=take,
        skip=skip,
        sort_direction=sort_direction,
        order_by=order_by,
        search=search,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    connection_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
    take: Union[Unset, float] = 100.0,
    skip: Union[Unset, float] = 0.0,
    sort_direction: Union[Unset, GetListUsersSortDirection] = "ASC",
    order_by: Union[Unset, GetListUsersOrderBy] = "name",
    search: Union[Unset, str] = UNSET,
) -> Optional[CCPaginatedConnectionUsersResponseDto]:
    """List users

     Get users for connection

    Args:
        connection_id (str):
        tenant_id (str):
        take (Union[Unset, float]):  Default: 100.0.
        skip (Union[Unset, float]):  Default: 0.0.
        sort_direction (Union[Unset, GetListUsersSortDirection]):  Default: 'ASC'.
        order_by (Union[Unset, GetListUsersOrderBy]):  Default: 'name'.
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CCPaginatedConnectionUsersResponseDto
    """

    return (
        await asyncio_detailed(
            connection_id=connection_id,
            client=client,
            tenant_id=tenant_id,
            take=take,
            skip=skip,
            sort_direction=sort_direction,
            order_by=order_by,
            search=search,
        )
    ).parsed
