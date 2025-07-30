from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cc_iso_country import CCIsoCountry
from ...types import UNSET, Response


def _get_kwargs(
    connection_id: str,
    *,
    tenant_id: str,
    code: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["tenantId"] = tenant_id

    params["code"] = code

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/v1/cloud/ms365/connections/{connection_id}/iso-country",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["CCIsoCountry"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CCIsoCountry.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["CCIsoCountry"]]:
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
    code: str,
) -> Response[list["CCIsoCountry"]]:
    """Remove M365 approved country

     Delete iso country from ms365 connection authorized country list

    Args:
        connection_id (str):
        tenant_id (str):
        code (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CCIsoCountry']]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
        tenant_id=tenant_id,
        code=code,
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
    code: str,
) -> Optional[list["CCIsoCountry"]]:
    """Remove M365 approved country

     Delete iso country from ms365 connection authorized country list

    Args:
        connection_id (str):
        tenant_id (str):
        code (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CCIsoCountry']
    """

    return sync_detailed(
        connection_id=connection_id,
        client=client,
        tenant_id=tenant_id,
        code=code,
    ).parsed


async def asyncio_detailed(
    connection_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
    code: str,
) -> Response[list["CCIsoCountry"]]:
    """Remove M365 approved country

     Delete iso country from ms365 connection authorized country list

    Args:
        connection_id (str):
        tenant_id (str):
        code (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CCIsoCountry']]
    """

    kwargs = _get_kwargs(
        connection_id=connection_id,
        tenant_id=tenant_id,
        code=code,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    connection_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
    code: str,
) -> Optional[list["CCIsoCountry"]]:
    """Remove M365 approved country

     Delete iso country from ms365 connection authorized country list

    Args:
        connection_id (str):
        tenant_id (str):
        code (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CCIsoCountry']
    """

    return (
        await asyncio_detailed(
            connection_id=connection_id,
            client=client,
            tenant_id=tenant_id,
            code=code,
        )
    ).parsed
