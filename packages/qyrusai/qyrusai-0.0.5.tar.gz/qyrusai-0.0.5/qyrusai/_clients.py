# from nova import AsyncNova
from typing import Optional
from .nova import AsyncNova, SyncNova
from .api_builder.api_builder import AsyncApiBuilder,SyncApiBuilder
from .data_amplifier.data_amplifier import AsyncDataAmplifier, SyncDataAmplifier
from .api_assertions import AsyncAssertions, SyncAssertions
from .vision_nova import Async_Vision_Nova, Sync_Vision_Nova
from .llm_evaluator import AsyncEvaluator, SyncEvaluator

class AsyncQyrusAI:

    # def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
    def __init__(self, api_key: str) -> None:
        self.nova = AsyncNova(api_key)
        self.api_builder = AsyncApiBuilder(api_key)
        self.data_amplifier = AsyncDataAmplifier(api_key)
        self.api_assertions = AsyncAssertions(api_key)
        self.vision_nova = Async_Vision_Nova(api_key)
        self.llm_evaluator = AsyncEvaluator(api_key)

class SyncQyrusAI:

    # def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
    def __init__(self, api_key: str) -> None:
        self.nova = SyncNova(api_key)
        self.api_builder = SyncApiBuilder(api_key)
        self.data_amplifier = SyncDataAmplifier(api_key)
        self.api_assertions = SyncAssertions(api_key)
        self.vision_nova = Sync_Vision_Nova(api_key)
        self.llm_evaluator = SyncEvaluator(api_key)
