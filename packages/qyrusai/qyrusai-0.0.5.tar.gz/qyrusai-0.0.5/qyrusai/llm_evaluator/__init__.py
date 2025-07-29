from typing import Optional
from .evaluator import AsyncLLMEvaluator, SyncLLMEvaluator


class AsyncEvaluator:

    def __init__(self, api_key: str):
        self.evaluator = AsyncLLMEvaluator(api_key)


class SyncEvaluator:

    def __init__(self, api_key: str):
        self.evaluator = SyncLLMEvaluator(api_key)
