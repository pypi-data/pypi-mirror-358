from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cc_cisco_duo_onboarding_state_dto import CCCiscoDuoOnboardingStateDto
from ...types import UNSET, Response


def _get_kwargs(
    *,
    tenant_id: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["tenantId"] = tenant_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/cloud/cisco/onboardings",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["CCCiscoDuoOnboardingStateDto"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CCCiscoDuoOnboardingStateDto.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["CCCiscoDuoOnboardingStateDto"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Response[list["CCCiscoDuoOnboardingStateDto"]]:
    """List Cisco onboardings

     List the states of the onboardings a customer has completed or in progress

    Args:
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CCCiscoDuoOnboardingStateDto']]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Optional[list["CCCiscoDuoOnboardingStateDto"]]:
    """List Cisco onboardings

     List the states of the onboardings a customer has completed or in progress

    Args:
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CCCiscoDuoOnboardingStateDto']
    """

    return sync_detailed(
        client=client,
        tenant_id=tenant_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Response[list["CCCiscoDuoOnboardingStateDto"]]:
    """List Cisco onboardings

     List the states of the onboardings a customer has completed or in progress

    Args:
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['CCCiscoDuoOnboardingStateDto']]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Optional[list["CCCiscoDuoOnboardingStateDto"]]:
    """List Cisco onboardings

     List the states of the onboardings a customer has completed or in progress

    Args:
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['CCCiscoDuoOnboardingStateDto']
    """

    return (
        await asyncio_detailed(
            client=client,
            tenant_id=tenant_id,
        )
    ).parsed
