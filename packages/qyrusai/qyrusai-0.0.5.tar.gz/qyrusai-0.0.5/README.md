# QyrusAI Python SDK

The **QyrusAI Python SDK** provides a _Python client_ to access our **_SOTA Single Use testing Agents_** for _test case generation_, _test data generation_, _API test case generation_, and many more.

## Key Features

- **Nova:** Nova provides a quick and easy way to generate test scenarios and test cases using JIRA tickets, User story documents and Rally Tickets. 
- **Nova API Assertions:** Nova API Assertions provide a quick way to create assertions to test API responses. These assertions include _header, schema, JSON Path, and JSON Body_ test cases.
- **API Builder**: API builder helps in visualizing virtualized APIs and provide a well planned Swagger documentation with APIs for the provided use case description. 
- **Vision Nova**: Vision Nova helps in creating functional tests from Figma design frames.
- **Data Amplification**: Data Amplification helps create highly realistic context specific data for testing needs.

## Installation

You can install `qyrusai` from the source as of now.

### From Source

```
pip install git+https://github.com/QQyrus/qyrusai-sdk.git
```

## Usage

The following is a basic example of how one can create test scenarios using **NOVA** using `qyrusai` SDK.

### Create Tests for JIRA Ticket

```py
from qyrusai import AsyncQyrusAI

async def jira():
    at = "your_api_key"
    client = AsyncQyrusAI(api_key=at)
    jira_endpoint = "your jira endpoint"
    jira_api_token = "your jira token"
    jira_username = "your jira email"
    jira_id = "your jira ticket id"
    op = await client.nova.from_jira.create(
        jira_api_token=jira_api_token,
        jira_endpoint=jira_endpoint,
        jira_username=jira_username,
        jira_id=jira_id)
    return op

if __name__ == "__main__":
    import asyncio
    print(asyncio.run(main_test()))
```
> Note : In the above example, `at` is supposed to store your secret key (api_key). In case you do not have it use the custom access token instead.

### Create Test via User Document

```py
from qyrusai import AsyncQyrusAI

async def main_test():
    at = "your_api_key"
    client = AsyncQyrusAI(api_key=at)
    op = await client.nova.from_description.create(
        "Create tests for login page")
    return op


if __name__ == "__main__":
    import asyncio
    print(asyncio.run(main_test()))
```
> Note : In the above example, `at` is supposed to store your secret key (api_key). In case you do not have it use the custom access token instead.

> Note : Both Asynchronous and Synchronous interactions are available now.
