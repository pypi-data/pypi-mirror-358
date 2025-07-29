from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.tev1_contact_group_dto import TEV1ContactGroupDto
from ...models.tev1_create_contact_group_request_dto import TEV1CreateContactGroupRequestDto
from ...types import Response


def _get_kwargs(
    account_id: str,
    *,
    body: TEV1CreateContactGroupRequestDto,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/accounts/{account_id}/contact-groups",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[TEV1ContactGroupDto]:
    if response.status_code == 200:
        response_200 = TEV1ContactGroupDto.from_dict(response.json())

        return response_200
    if response.status_code == 201:
        response_201 = TEV1ContactGroupDto.from_dict(response.json())

        return response_201
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
    *,
    client: AuthenticatedClient,
    body: TEV1CreateContactGroupRequestDto,
) -> Response[TEV1ContactGroupDto]:
    """Create contact group

    Args:
        account_id (str):
        body (TEV1CreateContactGroupRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1ContactGroupDto]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_id: str,
    *,
    client: AuthenticatedClient,
    body: TEV1CreateContactGroupRequestDto,
) -> Optional[TEV1ContactGroupDto]:
    """Create contact group

    Args:
        account_id (str):
        body (TEV1CreateContactGroupRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1ContactGroupDto
    """

    return sync_detailed(
        account_id=account_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    account_id: str,
    *,
    client: AuthenticatedClient,
    body: TEV1CreateContactGroupRequestDto,
) -> Response[TEV1ContactGroupDto]:
    """Create contact group

    Args:
        account_id (str):
        body (TEV1CreateContactGroupRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TEV1ContactGroupDto]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str,
    *,
    client: AuthenticatedClient,
    body: TEV1CreateContactGroupRequestDto,
) -> Optional[TEV1ContactGroupDto]:
    """Create contact group

    Args:
        account_id (str):
        body (TEV1CreateContactGroupRequestDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TEV1ContactGroupDto
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            client=client,
            body=body,
        )
    ).parsed
