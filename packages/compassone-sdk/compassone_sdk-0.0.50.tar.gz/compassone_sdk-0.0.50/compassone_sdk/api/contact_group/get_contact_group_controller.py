from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.tev1_contact_group_dto import TEV1ContactGroupDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    account_id: str,
    contact_group_id: str,
    *,
    include_members: Union[Unset, bool] = UNSET,
    include_assigned_tenants: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["includeMembers"] = include_members

    params["includeAssignedTenants"] = include_assigned_tenants

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/accounts/{account_id}/contact-groups/{contact_group_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[TEV1ContactGroupDto]:
    if response.status_code == 200:
        response_200 = TEV1ContactGroupDto.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[TEV1ContactGroupDto]:
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
    include_members: Union[Unset, bool] = UNSET,
    include_assigned_tenants: Union[Unset, bool] = UNSET,
) -> Response[TEV1ContactGroupDto]:
    """Get contact group by Id

    Args:
        account_id (str):
        contact_group_id (str):
        include_members (Union[Unset, bool]):
        include_assigned_tenants (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1ContactGroupDto]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        contact_group_id=contact_group_id,
        include_members=include_members,
        include_assigned_tenants=include_assigned_tenants,
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
    include_members: Union[Unset, bool] = UNSET,
    include_assigned_tenants: Union[Unset, bool] = UNSET,
) -> Optional[TEV1ContactGroupDto]:
    """Get contact group by Id

    Args:
        account_id (str):
        contact_group_id (str):
        include_members (Union[Unset, bool]):
        include_assigned_tenants (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1ContactGroupDto
    """

    return sync_detailed(
        account_id=account_id,
        contact_group_id=contact_group_id,
        client=client,
        include_members=include_members,
        include_assigned_tenants=include_assigned_tenants,
    ).parsed


async def asyncio_detailed(
    account_id: str,
    contact_group_id: str,
    *,
    client: AuthenticatedClient,
    include_members: Union[Unset, bool] = UNSET,
    include_assigned_tenants: Union[Unset, bool] = UNSET,
) -> Response[TEV1ContactGroupDto]:
    """Get contact group by Id

    Args:
        account_id (str):
        contact_group_id (str):
        include_members (Union[Unset, bool]):
        include_assigned_tenants (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1ContactGroupDto]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        contact_group_id=contact_group_id,
        include_members=include_members,
        include_assigned_tenants=include_assigned_tenants,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str,
    contact_group_id: str,
    *,
    client: AuthenticatedClient,
    include_members: Union[Unset, bool] = UNSET,
    include_assigned_tenants: Union[Unset, bool] = UNSET,
) -> Optional[TEV1ContactGroupDto]:
    """Get contact group by Id

    Args:
        account_id (str):
        contact_group_id (str):
        include_members (Union[Unset, bool]):
        include_assigned_tenants (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1ContactGroupDto
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            contact_group_id=contact_group_id,
            client=client,
            include_members=include_members,
            include_assigned_tenants=include_assigned_tenants,
        )
    ).parsed
