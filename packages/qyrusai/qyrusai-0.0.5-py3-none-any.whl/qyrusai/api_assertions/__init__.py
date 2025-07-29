from typing import Optional
from .headers import AsyncHeaderAssertions,SyncHeaderAssertions
from .json_body import AsyncJSONBodyAssertions,SyncJSONBodyAssertions
from .json_path import AsyncJSONPathAssertions,SyncJSONPathAssertions
from .json_schema import AsyncJSONSchemaAssertions,SyncJSONSchemaAssertions
from .all_assertions import AsyncAllAssertions,SyncAllAssertions

class AsyncAssertions:
    def __init__(self, api_key: str) -> None:
        self.headers = AsyncHeaderAssertions(api_key)
        self.jsonbody = AsyncJSONBodyAssertions(api_key)
        self.jsonpath = AsyncJSONPathAssertions(api_key)
        self.jsonschema = AsyncJSONSchemaAssertions(api_key)
        self.all_assertions = AsyncAllAssertions(api_key)
        
class SyncAssertions:
    def __init__(self, api_key: str) -> None:
        self.headers = SyncHeaderAssertions(api_key)
        self.jsonbody = SyncJSONBodyAssertions(api_key)
        self.jsonpath = SyncJSONPathAssertions(api_key)
        self.jsonschema = SyncJSONSchemaAssertions(api_key)
        self.all_assertions = SyncAllAssertions(api_key)