from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_account_controller_list_partnership_type import (
    GetAccountControllerListPartnershipType,
)
from ...models.get_account_controller_list_sort_by import (
    GetAccountControllerListSortBy,
)
from ...models.te_order_direction import TEOrderDirection
from ...models.tev1_paginated_accounts_response_dto import TEV1PaginatedAccountsResponseDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetAccountControllerListSortBy] = "name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    billing_version: Union[Unset, str] = UNSET,
    partnership_type: Union[Unset, GetAccountControllerListPartnershipType] = UNSET,
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

    params["billingVersion"] = billing_version

    json_partnership_type: Union[Unset, str] = UNSET
    if not isinstance(partnership_type, Unset):
        json_partnership_type = partnership_type

    params["partnershipType"] = json_partnership_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/accounts",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[TEV1PaginatedAccountsResponseDto]:
    if response.status_code == 200:
        response_200 = TEV1PaginatedAccountsResponseDto.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[TEV1PaginatedAccountsResponseDto]:
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
    sort_by: Union[Unset, GetAccountControllerListSortBy] = "name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    billing_version: Union[Unset, str] = UNSET,
    partnership_type: Union[Unset, GetAccountControllerListPartnershipType] = UNSET,
) -> Response[TEV1PaginatedAccountsResponseDto]:
    """List accounts

    Args:
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetAccountControllerListSortBy]):  Default: 'name'.
        sort_order (Union[Unset, TEOrderDirection]):
        billing_version (Union[Unset, str]):
        partnership_type (Union[Unset, GetAccountControllerListPartnershipType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1PaginatedAccountsResponseDto]
    """

    kwargs = _get_kwargs(
        page_size=page_size,
        page=page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        billing_version=billing_version,
        partnership_type=partnership_type,
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
    sort_by: Union[Unset, GetAccountControllerListSortBy] = "name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    billing_version: Union[Unset, str] = UNSET,
    partnership_type: Union[Unset, GetAccountControllerListPartnershipType] = UNSET,
) -> Optional[TEV1PaginatedAccountsResponseDto]:
    """List accounts

    Args:
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetAccountControllerListSortBy]):  Default: 'name'.
        sort_order (Union[Unset, TEOrderDirection]):
        billing_version (Union[Unset, str]):
        partnership_type (Union[Unset, GetAccountControllerListPartnershipType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1PaginatedAccountsResponseDto
    """

    return sync_detailed(
        client=client,
        page_size=page_size,
        page=page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        billing_version=billing_version,
        partnership_type=partnership_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetAccountControllerListSortBy] = "name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    billing_version: Union[Unset, str] = UNSET,
    partnership_type: Union[Unset, GetAccountControllerListPartnershipType] = UNSET,
) -> Response[TEV1PaginatedAccountsResponseDto]:
    """List accounts

    Args:
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetAccountControllerListSortBy]):  Default: 'name'.
        sort_order (Union[Unset, TEOrderDirection]):
        billing_version (Union[Unset, str]):
        partnership_type (Union[Unset, GetAccountControllerListPartnershipType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1PaginatedAccountsResponseDto]
    """

    kwargs = _get_kwargs(
        page_size=page_size,
        page=page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        billing_version=billing_version,
        partnership_type=partnership_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, float] = 50.0,
    page: Union[Unset, float] = 1.0,
    search: Union[Unset, str] = "",
    sort_by: Union[Unset, GetAccountControllerListSortBy] = "name",
    sort_order: Union[Unset, TEOrderDirection] = UNSET,
    billing_version: Union[Unset, str] = UNSET,
    partnership_type: Union[Unset, GetAccountControllerListPartnershipType] = UNSET,
) -> Optional[TEV1PaginatedAccountsResponseDto]:
    """List accounts

    Args:
        page_size (Union[Unset, float]):  Default: 50.0.
        page (Union[Unset, float]):  Default: 1.0.
        search (Union[Unset, str]):  Default: ''.
        sort_by (Union[Unset, GetAccountControllerListSortBy]):  Default: 'name'.
        sort_order (Union[Unset, TEOrderDirection]):
        billing_version (Union[Unset, str]):
        partnership_type (Union[Unset, GetAccountControllerListPartnershipType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1PaginatedAccountsResponseDto
    """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            page=page,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            billing_version=billing_version,
            partnership_type=partnership_type,
        )
    ).parsed
