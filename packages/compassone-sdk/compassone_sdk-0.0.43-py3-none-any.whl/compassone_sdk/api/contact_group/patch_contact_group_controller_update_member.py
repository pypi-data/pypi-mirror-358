from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.tev1_contact_group_member_dto import TEV1ContactGroupMemberDto
from ...models.tev1_update_contact_group_member_request_dto import TEV1UpdateContactGroupMemberRequestDto
from ...types import Response


def _get_kwargs(
    account_id: str,
    contact_group_id: str,
    member_id: str,
    *,
    body: TEV1UpdateContactGroupMemberRequestDto,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/v1/accounts/{account_id}/contact-groups/{contact_group_id}/members/{member_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[TEV1ContactGroupMemberDto]:
    if response.status_code == 200:
        response_200 = TEV1ContactGroupMemberDto.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[TEV1ContactGroupMemberDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    account_id: str,
    contact_group_id: str,
    member_id: str,
    *,
    client: AuthenticatedClient,
    body: TEV1UpdateContactGroupMemberRequestDto,
) -> Response[TEV1ContactGroupMemberDto]:
    """Update member for contact group

    Args:
        account_id (str):
        contact_group_id (str):
        member_id (str):
        body (TEV1UpdateContactGroupMemberRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1ContactGroupMemberDto]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        contact_group_id=contact_group_id,
        member_id=member_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_id: str,
    contact_group_id: str,
    member_id: str,
    *,
    client: AuthenticatedClient,
    body: TEV1UpdateContactGroupMemberRequestDto,
) -> Optional[TEV1ContactGroupMemberDto]:
    """Update member for contact group

    Args:
        account_id (str):
        contact_group_id (str):
        member_id (str):
        body (TEV1UpdateContactGroupMemberRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1ContactGroupMemberDto
    """

    return sync_detailed(
        account_id=account_id,
        contact_group_id=contact_group_id,
        member_id=member_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    account_id: str,
    contact_group_id: str,
    member_id: str,
    *,
    client: AuthenticatedClient,
    body: TEV1UpdateContactGroupMemberRequestDto,
) -> Response[TEV1ContactGroupMemberDto]:
    """Update member for contact group

    Args:
        account_id (str):
        contact_group_id (str):
        member_id (str):
        body (TEV1UpdateContactGroupMemberRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1ContactGroupMemberDto]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        contact_group_id=contact_group_id,
        member_id=member_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str,
    contact_group_id: str,
    member_id: str,
    *,
    client: AuthenticatedClient,
    body: TEV1UpdateContactGroupMemberRequestDto,
) -> Optional[TEV1ContactGroupMemberDto]:
    """Update member for contact group

    Args:
        account_id (str):
        contact_group_id (str):
        member_id (str):
        body (TEV1UpdateContactGroupMemberRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1ContactGroupMemberDto
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            contact_group_id=contact_group_id,
            member_id=member_id,
            client=client,
            body=body,
        )
    ).parsed
