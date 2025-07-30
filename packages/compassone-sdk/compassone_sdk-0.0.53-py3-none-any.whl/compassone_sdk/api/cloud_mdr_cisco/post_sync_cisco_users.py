from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cc_cisco_duo_onboarding_state_dto import CCCiscoDuoOnboardingStateDto
from ...types import UNSET, Response


def _get_kwargs(
    onboarding_id: str,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["tenantId"] = tenant_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/cloud/cisco/onboardings/{onboarding_id}/post-provision",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[CCCiscoDuoOnboardingStateDto]:
    if response.status_code == 201:
        response_201 = CCCiscoDuoOnboardingStateDto.from_dict(response.json())

        return response_201
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[CCCiscoDuoOnboardingStateDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    onboarding_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Response[CCCiscoDuoOnboardingStateDto]:
    """Sync Cisco users

     Verifies the domain-wide delegation permissions were configured correctly and start syncing users
    (if sync job not started yet or stalled).

    Args:
        onboarding_id (str):
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CCCiscoDuoOnboardingStateDto]
    """

    kwargs = _get_kwargs(
        onboarding_id=onboarding_id,
        tenant_id=tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    onboarding_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Optional[CCCiscoDuoOnboardingStateDto]:
    """Sync Cisco users

     Verifies the domain-wide delegation permissions were configured correctly and start syncing users
    (if sync job not started yet or stalled).

    Args:
        onboarding_id (str):
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CCCiscoDuoOnboardingStateDto
    """

    return sync_detailed(
        onboarding_id=onboarding_id,
        client=client,
        tenant_id=tenant_id,
    ).parsed


async def asyncio_detailed(
    onboarding_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Response[CCCiscoDuoOnboardingStateDto]:
    """Sync Cisco users

     Verifies the domain-wide delegation permissions were configured correctly and start syncing users
    (if sync job not started yet or stalled).

    Args:
        onboarding_id (str):
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CCCiscoDuoOnboardingStateDto]
    """

    kwargs = _get_kwargs(
        onboarding_id=onboarding_id,
        tenant_id=tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    onboarding_id: str,
    *,
    client: AuthenticatedClient,
    tenant_id: str,
) -> Optional[CCCiscoDuoOnboardingStateDto]:
    """Sync Cisco users

     Verifies the domain-wide delegation permissions were configured correctly and start syncing users
    (if sync job not started yet or stalled).

    Args:
        onboarding_id (str):
        tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CCCiscoDuoOnboardingStateDto
    """

    return (
        await asyncio_detailed(
            onboarding_id=onboarding_id,
            client=client,
            tenant_id=tenant_id,
        )
    ).parsed
