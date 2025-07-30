from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_contact_group_controller_get_unassigned_tenants_sort_by import (
    GetContactGroupControllerGetUnassignedTenantsSortBy,
)
from ...models.te_order_direction import TEOrderDirection
from ...models.tev1_paginated_tenant_with_contact_group_minimal_response_dto import (
    TEV1PaginatedTenantWithContactGroupMinimalResponseDto,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    account_id: str,
    contact_group_id: str,
    *,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetContactGroupControllerGetUnassignedTenantsSortBy] = "tenant.name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
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

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/accounts/{account_id}/contact-groups/{contact_group_id}/unassigned-tenants",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[TEV1PaginatedTenantWithContactGroupMinimalResponseDto]:
    if response.status_code == 200:
        response_200 = TEV1PaginatedTenantWithContactGroupMinimalResponseDto.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[TEV1PaginatedTenantWithContactGroupMinimalResponseDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    account_id: str,
    contact_group_id: str,
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetContactGroupControllerGetUnassignedTenantsSortBy] = "tenant.name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
) -> Response[TEV1PaginatedTenantWithContactGroupMinimalResponseDto]:
    """Get tenants unassigned to contact group

     Get a paginated list of all tenants which have not being assigned to a given contact group

    Args:
        account_id (str):
        contact_group_id (str):
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetContactGroupControllerGetUnassignedTenantsSortBy]):  Default:
            'tenant.name'.
        sort_order (Union[Unset, TEOrderDirection]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1PaginatedTenantWithContactGroupMinimalResponseDto]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        contact_group_id=contact_group_id,
        page_size=page_size,
        page=page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_id: str,
    contact_group_id: str,
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetContactGroupControllerGetUnassignedTenantsSortBy] = "tenant.name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
) -> Optional[TEV1PaginatedTenantWithContactGroupMinimalResponseDto]:
    """Get tenants unassigned to contact group

     Get a paginated list of all tenants which have not being assigned to a given contact group

    Args:
        account_id (str):
        contact_group_id (str):
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetContactGroupControllerGetUnassignedTenantsSortBy]):  Default:
            'tenant.name'.
        sort_order (Union[Unset, TEOrderDirection]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1PaginatedTenantWithContactGroupMinimalResponseDto
    """

    return sync_detailed(
        account_id=account_id,
        contact_group_id=contact_group_id,
        client=client,
        page_size=page_size,
        page=page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    account_id: str,
    contact_group_id: str,
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetContactGroupControllerGetUnassignedTenantsSortBy] = "tenant.name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
) -> Response[TEV1PaginatedTenantWithContactGroupMinimalResponseDto]:
    """Get tenants unassigned to contact group

     Get a paginated list of all tenants which have not being assigned to a given contact group

    Args:
        account_id (str):
        contact_group_id (str):
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetContactGroupControllerGetUnassignedTenantsSortBy]):  Default:
            'tenant.name'.
        sort_order (Union[Unset, TEOrderDirection]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1PaginatedTenantWithContactGroupMinimalResponseDto]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        contact_group_id=contact_group_id,
        page_size=page_size,
        page=page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str,
    contact_group_id: str,
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetContactGroupControllerGetUnassignedTenantsSortBy] = "tenant.name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
) -> Optional[TEV1PaginatedTenantWithContactGroupMinimalResponseDto]:
    """Get tenants unassigned to contact group

     Get a paginated list of all tenants which have not being assigned to a given contact group

    Args:
        account_id (str):
        contact_group_id (str):
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetContactGroupControllerGetUnassignedTenantsSortBy]):  Default:
            'tenant.name'.
        sort_order (Union[Unset, TEOrderDirection]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1PaginatedTenantWithContactGroupMinimalResponseDto
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            contact_group_id=contact_group_id,
            client=client,
            page_size=page_size,
            page=page,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
