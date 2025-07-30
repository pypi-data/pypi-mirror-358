from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_contact_group_controller_list_sort_by import (
    GetContactGroupControllerListSortBy,
)
from ...models.te_order_direction import TEOrderDirection
from ...models.tev1_paginated_contact_group_response_dto import TEV1PaginatedContactGroupResponseDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    account_id: str,
    *,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetContactGroupControllerListSortBy] = "contactGroup.name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    tenants_page_size: Union[Unset, float] = 0.0,
    members_page_size: Union[Unset, float] = 0.0,
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

    params["tenantsPageSize"] = tenants_page_size

    params["membersPageSize"] = members_page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/accounts/{account_id}/contact-groups",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[TEV1PaginatedContactGroupResponseDto]:
    if response.status_code == 200:
        response_200 = TEV1PaginatedContactGroupResponseDto.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[TEV1PaginatedContactGroupResponseDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    account_id: str,
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetContactGroupControllerListSortBy] = "contactGroup.name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    tenants_page_size: Union[Unset, float] = 0.0,
    members_page_size: Union[Unset, float] = 0.0,
) -> Response[TEV1PaginatedContactGroupResponseDto]:
    """List contact groups

    Args:
        account_id (str):
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetContactGroupControllerListSortBy]):  Default:
            'contactGroup.name'.
        sort_order (Union[Unset, TEOrderDirection]):
        tenants_page_size (Union[Unset, float]):  Default: 0.0.
        members_page_size (Union[Unset, float]):  Default: 0.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1PaginatedContactGroupResponseDto]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        page_size=page_size,
        page=page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        tenants_page_size=tenants_page_size,
        members_page_size=members_page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_id: str,
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetContactGroupControllerListSortBy] = "contactGroup.name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    tenants_page_size: Union[Unset, float] = 0.0,
    members_page_size: Union[Unset, float] = 0.0,
) -> Optional[TEV1PaginatedContactGroupResponseDto]:
    """List contact groups

    Args:
        account_id (str):
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetContactGroupControllerListSortBy]):  Default:
            'contactGroup.name'.
        sort_order (Union[Unset, TEOrderDirection]):
        tenants_page_size (Union[Unset, float]):  Default: 0.0.
        members_page_size (Union[Unset, float]):  Default: 0.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1PaginatedContactGroupResponseDto
    """

    return sync_detailed(
        account_id=account_id,
        client=client,
        page_size=page_size,
        page=page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        tenants_page_size=tenants_page_size,
        members_page_size=members_page_size,
    ).parsed


async def asyncio_detailed(
    account_id: str,
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetContactGroupControllerListSortBy] = "contactGroup.name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    tenants_page_size: Union[Unset, float] = 0.0,
    members_page_size: Union[Unset, float] = 0.0,
) -> Response[TEV1PaginatedContactGroupResponseDto]:
    """List contact groups

    Args:
        account_id (str):
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetContactGroupControllerListSortBy]):  Default:
            'contactGroup.name'.
        sort_order (Union[Unset, TEOrderDirection]):
        tenants_page_size (Union[Unset, float]):  Default: 0.0.
        members_page_size (Union[Unset, float]):  Default: 0.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1PaginatedContactGroupResponseDto]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        page_size=page_size,
        page=page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        tenants_page_size=tenants_page_size,
        members_page_size=members_page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str,
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetContactGroupControllerListSortBy] = "contactGroup.name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    tenants_page_size: Union[Unset, float] = 0.0,
    members_page_size: Union[Unset, float] = 0.0,
) -> Optional[TEV1PaginatedContactGroupResponseDto]:
    """List contact groups

    Args:
        account_id (str):
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetContactGroupControllerListSortBy]):  Default:
            'contactGroup.name'.
        sort_order (Union[Unset, TEOrderDirection]):
        tenants_page_size (Union[Unset, float]):  Default: 0.0.
        members_page_size (Union[Unset, float]):  Default: 0.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1PaginatedContactGroupResponseDto
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            client=client,
            page_size=page_size,
            page=page,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            tenants_page_size=tenants_page_size,
            members_page_size=members_page_size,
        )
    ).parsed
