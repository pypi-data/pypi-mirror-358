from qyrusai.configs import Configurations
from typing import Optional
from urllib.parse import urljoin
from qyrusai._rest import AsyncHTTPClient, SyncHTTPClient


class Async_VisionNova_create:

    def __init__(self, api_key: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        token_valid = Configurations.verifyToken(api_key) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = gatewayDetails.get("gatewayUrl")
        self.gateway_token = gatewayDetails.get("gatewayToken")

    async def generate(self, image_url: str):
        """Give image url to generate test scenario generation.

        Args:
            image_url (str): image_url.
        """
        url = urljoin(
            self.base_url,
            Configurations.getVisionNovaContextPath("json-create-tests"))
        data = {
            "image_url": image_url,
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer "+self.gateway_token,
            'Custom': self.api_key
        }

        async_client = AsyncHTTPClient()
        response_data = await async_client.post(url, data, headers)

        # print(
        #     f"response_data for generate [ASYNC] (vision nova) : {response_data}"
        # )
        # print(
        #     f"response_data for generate [ASYNC] (vision nova) TYPE == >> : {type(response_data)}"
        # )

        return response_data


class Sync_VisionNova_create:

    def __init__(self, api_key: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        token_valid = Configurations.verifyToken(api_key) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = gatewayDetails.get("gatewayUrl")
        self.gateway_token = gatewayDetails.get("gatewayToken")

    def generate(self, image_url: str):
        """Give image url to generate test scenario generation.

        Args:
            image_url (str): image_url.
        """
        url = urljoin(
            self.base_url,
            Configurations.getVisionNovaContextPath("json-create-tests"))
        data = {
            "image_url": image_url,
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer "+self.gateway_token,
            'Custom': self.api_key
        }

        sync_client = SyncHTTPClient()
        response_data = sync_client.post(url, data, headers)

        # print(
        #     f"response_data for generate [ASYNC] (vision nova) : {response_data}"
        # )
        # print(
        #     f"response_data for generate [ASYNC] (vision nova) TYPE == >> : {type(response_data)}"
        # )

        return response_data


class Async_VisionNova_verify:

    def __init__(self, api_key: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        token_valid = Configurations.verifyToken(api_key) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = gatewayDetails.get("gatewayUrl")
        self.gateway_token = gatewayDetails.get("gatewayToken")

    async def verify(self, image_url: str):
        """Give image url to verify visual accessibility analysis.

        Args:
            image_url (str): image_url.
        """
        url = urljoin(
            self.base_url,
            Configurations.getVisionNovaContextPath(
                "json-accessibility-comment"))
        data = {
            "image_url": image_url,
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer "+self.gateway_token,
            'Custom': self.api_key
        }

        async_client = AsyncHTTPClient()
        response_data = await async_client.post(url, data, headers)

        # print(
        #     f"response_data for verify [ASYNC] (vision nova) : {response_data}"
        # )
        # print(
        #     f"response_data for verify [ASYNC] (vision nova) TYPE == >> : {type(response_data)}"
        # )

        return response_data


class Sync_VisionNova_verify:

    def __init__(self, api_key: str):
        self.api_key = api_key
        # token_valid = asyncio.run(Configurations.verifyToken(api_key)) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        token_valid = Configurations.verifyToken(api_key) # If True is stored, well and good otherwise an Exception will have been raised already if something goes wrong.
        if not token_valid:
            raise Exception("401")
        gatewayDetails = Configurations.getDefaultGateway(api_key)
        # gatewayDetails = asyncio.run(Configurations.getDefaultGateway(api_key))
        self.base_url = gatewayDetails.get("gatewayUrl")
        self.gateway_token = gatewayDetails.get("gatewayToken")

    def verify(self, image_url: str):
        """Give image url to verify visual accessibility analysis.

        Args:
            image_url (str): image_url.
        """
        url = urljoin(
            self.base_url,
            Configurations.getVisionNovaContextPath(
                "json-accessibility-comment"))
        data = {
            "image_url": image_url,
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer "+self.gateway_token,
            'Custom': self.api_key
        }

        sync_client = SyncHTTPClient()
        response_data = sync_client.post(url, data, headers)

        # print(
        #     f"response_data for verify [SYNC] (vision nova) : {response_data}")
        # print(
        #     f"response_data for verify [SYNC] (vision nova) TYPE == >> : {type(response_data)}"
        # )

        return response_data
