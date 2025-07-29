from qyrusai.configs import Configurations
from typing import Optional
from urllib.parse import urljoin
from qyrusai._rest import AsyncHTTPClient, SyncHTTPClient
from typing import Optional, List

class AsyncLLMEvaluator:

    def __init__(self, api_key: str):
        self.api_key = api_key
        token_valid = Configurations.verifyToken(api_key)
        if not token_valid:
            raise Exception("401")
        gatewayDetails = Configurations.getDefaultGateway(api_key)
        self.base_url = gatewayDetails.get("gatewayUrl")
        self.gateway_token = gatewayDetails.get("gatewayToken")

    async def evaluate(self,
                       context: str,
                       expected_output: str,
                       executed_output: List[str],
                       guardrails: Optional[str] = None) -> float:
        url = urljoin(self.base_url, Configurations.getLLMEvaluatorContextPath("judge"))
        # url = Configurations.getLLMEvaluatorContextPath("judge")

        data = {
            "context": context,
            "expected_output": expected_output,
            "executed_output": executed_output,
            "guardrails": guardrails
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }
        async_client = AsyncHTTPClient()
        response = await async_client.post(url, data, headers)
        return response


class SyncLLMEvaluator:

    def __init__(self, api_key: str):
        self.api_key = api_key
        token_valid = Configurations.verifyToken(api_key)
        if not token_valid:
            raise Exception("401")
        gatewayDetails = Configurations.getDefaultGateway(api_key)
        self.base_url = gatewayDetails.get("gatewayUrl")
        self.gateway_token = gatewayDetails.get("gatewayToken")

    def evaluate(self,
                 context: str,
                 expected_output: str,
                 executed_output: List[str],
                 guardrails: Optional[str] = None) -> float:
        url = urljoin(self.base_url, Configurations.getLLMEvaluatorContextPath("judge"))
        # url = Configurations.getLLMEvaluatorContextPath("judge")

        data = {
            "context": context,
            "expected_output": expected_output,
            "executed_output": executed_output,
            "guardrails": guardrails
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }
        sync_client = SyncHTTPClient()
        response = sync_client.post(url, data, headers)
        return response
