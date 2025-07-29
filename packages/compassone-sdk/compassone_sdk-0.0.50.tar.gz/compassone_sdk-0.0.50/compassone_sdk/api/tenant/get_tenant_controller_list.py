from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_tenant_controller_list_sort_by import (
    GetTenantControllerListSortBy,
)
from ...models.te_order_direction import TEOrderDirection
from ...models.tev1_paginated_tenants_response_dto import TEV1PaginatedTenantsResponseDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetTenantControllerListSortBy] = "id",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    account_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["pageSize"] = page_size

    params["page"] = page

    params["search"] = search

    json_sort_by: Union[Unset, str] = UNSET
    if not isinstance(sort_by, Unset):
        json_sort_by = sort_by

    params["sortBy"] = json_sort_by

    json_sort_order: Union[Unset, str] = UNSET
    if not isinstance(sort_order, Unset):
        json_sort_order = sort_order

    params["sortOrder"] = json_sort_order

    params["accountId"] = account_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/tenants",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[TEV1PaginatedTenantsResponseDto]:
    if response.status_code == 200:
        response_200 = TEV1PaginatedTenantsResponseDto.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[TEV1PaginatedTenantsResponseDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetTenantControllerListSortBy] = "id",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    account_id: Union[Unset, str] = UNSET,
) -> Response[TEV1PaginatedTenantsResponseDto]:
    """List tenants

    Args:
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetTenantControllerListSortBy]):  Default: 'id'.
        sort_order (Union[Unset, TEOrderDirection]):
        account_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1PaginatedTenantsResponseDto]
    """

    kwargs = _get_kwargs(
        page_size=page_size,
        page=page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        account_id=account_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetTenantControllerListSortBy] = "id",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    account_id: Union[Unset, str] = UNSET,
) -> Optional[TEV1PaginatedTenantsResponseDto]:
    """List tenants

    Args:
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetTenantControllerListSortBy]):  Default: 'id'.
        sort_order (Union[Unset, TEOrderDirection]):
        account_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1PaginatedTenantsResponseDto
    """

    return sync_detailed(
        client=client,
        page_size=page_size,
        page=page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        account_id=account_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetTenantControllerListSortBy] = "id",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    account_id: Union[Unset, str] = UNSET,
) -> Response[TEV1PaginatedTenantsResponseDto]:
    """List tenants

    Args:
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetTenantControllerListSortBy]):  Default: 'id'.
        sort_order (Union[Unset, TEOrderDirection]):
        account_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1PaginatedTenantsResponseDto]
    """

    kwargs = _get_kwargs(
        page_size=page_size,
        page=page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        account_id=account_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetTenantControllerListSortBy] = "id",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    account_id: Union[Unset, str] = UNSET,
) -> Optional[TEV1PaginatedTenantsResponseDto]:
    """List tenants

    Args:
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetTenantControllerListSortBy]):  Default: 'id'.
        sort_order (Union[Unset, TEOrderDirection]):
        account_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1PaginatedTenantsResponseDto
    """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            page=page,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            account_id=account_id,
        )
    ).parsed
