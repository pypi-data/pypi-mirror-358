from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response


def _get_kwargs(
    connection_id: str,
    user_id: str,
    iso_country_id: str,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["tenantId"] = tenant_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/v1/cloud/ms365/connections/{connection_id}/users/{user_id}/isoCountry/{iso_country_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[str]:
    if response.status_code == 200:
        response_200 = cast(str, response.json())
        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[str]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    connection_id: str,
    user_id: str,
    iso_country_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Response[str]:
    """Remove approved country for M365 user

     Deletes an authorized country from user

    Args:
        connection_id (str):
        user_id (str):
        iso_country_id (str):
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[str]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
        user_id=user_id,
        iso_country_id=iso_country_id,
        tenant_id=tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    connection_id: str,
    user_id: str,
    iso_country_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Optional[str]:
    """Remove approved country for M365 user

     Deletes an authorized country from user

    Args:
        connection_id (str):
        user_id (str):
        iso_country_id (str):
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        str
    """

    return sync_detailed(
        connection_id=connection_id,
        user_id=user_id,
        iso_country_id=iso_country_id,
        client=client,
        tenant_id=tenant_id,
    ).parsed


async def asyncio_detailed(
    connection_id: str,
    user_id: str,
    iso_country_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Response[str]:
    """Remove approved country for M365 user

     Deletes an authorized country from user

    Args:
        connection_id (str):
        user_id (str):
        iso_country_id (str):
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[str]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
        user_id=user_id,
        iso_country_id=iso_country_id,
        tenant_id=tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    connection_id: str,
    user_id: str,
    iso_country_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Optional[str]:
    """Remove approved country for M365 user

     Deletes an authorized country from user

    Args:
        connection_id (str):
        user_id (str):
        iso_country_id (str):
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        str
    """

    return (
        await asyncio_detailed(
            connection_id=connection_id,
            user_id=user_id,
            iso_country_id=iso_country_id,
            client=client,
            tenant_id=tenant_id,
        )
    ).parsed
