# CompassOne API Client for Python

The CompassOne API Client provides a Python-based interface to interact with the CompassOne public API. It simplifies the process of making API requests and handling responses with comprehensive type safety and multiple execution modes.

## Table of Contents

- [Python Version Compatibility](#python-version-compatibility)
- [Installation](#installation)
- [Usage](#usage)
    - [Creating a Client](#creating-a-client)
    - [Function Variants](#function-variants)
    - [Synchronous Usage](#synchronous-usage)
    - [Asynchronous Usage](#asynchronous-usage)
- [Error Handling](#error-handling)

## Python Version Compatibility

This client requires Python 3.7 or higher due to the use of:
- f-strings
- Type hints
- Modern exception handling
- Async/await syntax
- Other Python 3.7+ features

It is tested and supported on Python versions:
- 3.7
- 3.8
- 3.9
- 3.10
- 3.11
- 3.12
- 3.13

## Installation
Install the CompassOne API client for Python with the desired version, e.g., 1.2.3
```bash
pip install compassone-sdk=1.2.3
```

## Usage

### Creating a Client

To use the CompassOne API client, you first need to create an authenticated client instance:

```python
from compassone_sdk import AuthenticatedClient

COMPASS_ONE_API_URL="https://api.blackpointcyber.com"
COMPASS_ONE_API_TOKEN="your_api_token_here"

# Create an authenticated client instance with your API credentials
authenticated_client = AuthenticatedClient(base_url=COMPASS_ONE_API_URL, token=COMPASS_ONE_API_TOKEN)
```
### Function Variants

The CompassOne API client provides multiple function variants for each API endpoint to accommodate different use cases:

#### Available Function Variants

Each API endpoint offers the following variants:

- **`.sync_detailed()`**: Synchronous function that returns a detailed response object containing status code, headers, and parsed data
- **`.asyncio_detailed()`**: Asynchronous function that returns a detailed response object containing status code, headers, and parsed data

#### API Organization

The API functions are organized under the `compassone_sdk.api` package, grouped by resource categories:
- **Account APIs**: `compassone_sdk.api.account`
- **Tenant APIs**: `compassone_sdk.api.tenant`
- **Contact Group APIs**: `compassone_sdk.api.contact_group`
- **Cloud MDR APIs**: `compassone_sdk.api.cloud_mdr`
- **Cloud MDR Cisco APIs**: `compassone_sdk.api.cloud_mdr_cisco`
- **Cloud MDR Google APIs**: `compassone_sdk.api.cloud_mdr_google`
- **Cloud MDR M365 APIs**: `compassone_sdk.api.cloud_mdr_m365`


### Synchronous Usage Examples

#### Account API Examples

Here are examples of how to use the Account API endpoints synchronously:
```python
from compassone_sdk.api.account import get_account_controller_list
from compassone_sdk.models.tev1_paginated_accounts_response_dto import TEV1PaginatedAccountsResponseDto

# Make a synchronous API call to get the list of accounts
# This returns a detailed response object with status code, headers, and parsed data
# The 'client' parameter should be the authenticated_client instance created above
response = get_account_controller_list.sync_detailed(client=authenticated_client)

# response.parsed contains the parsed response data as a TEV1PaginatedAccountsResponseDto object
# This includes a list of accounts with pagination information
result: TEV1PaginatedAccountsResponseDto = response.parsed
```

### Synchronous Usage

#### Account API Examples

Here are examples of how to use the Account API endpoints synchronously:
```python
from compassone_sdk.api.account import get_account_controller_list

# Make a synchronous API call to get the list of accounts
# This returns a detailed response object with status code, headers, and parsed data
# The 'client' parameter should be the authenticated_client instance created above
response = get_account_controller_list.sync_detailed(client=authenticated_client)

# response.parsed contains the parsed response data as a TEV1PaginatedAccountsResponseDto object
# This includes a list of accounts with pagination information
result: TEV1PaginatedAccountsResponseDto = response.parsed
```

### Asynchronous Usage

#### Tenant API Examples

Here are examples of how to use the Tenant API endpoints asynchronously:
```python
import asyncio

from compassone_sdk.api.tenant import get_tenant_controller_list
from compassone_sdk.models.tev1_paginated_tenants_response_dto import TEV1PaginatedTenantsResponseDto

# Make a synchronous API call to get the list of accounts
# This returns a detailed response object with status code, headers, and parsed data
# The 'client' parameter should be the authenticated_client instance created above
response = asyncio.run(get_tenant_controller_list.asyncio_detailed(client=authenticated_client, account_id="your_account_id_here"))

# response.parsed contains the parsed response data as a TEV1PaginatedAccountsResponseDto object
# This includes a list of accounts with pagination information
result: TEV1PaginatedTenantsResponseDto = response.parsed
```

### Error Handling

All API methods in this SDK return a `Response` object, which contains the following attributes:
- `status_code`: The HTTP status code of the response.
- `content`: The raw response content as bytes.
- `headers`: The response headers.
- `parsed`: The parsed response data (or `None` if parsing failed or the response was not successful).

You should always check the `status_code` and/or the `parsed` attribute to determine if the request was successful. For convenience
