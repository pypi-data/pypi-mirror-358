from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union


# Pydantic for Input and Response
class Scenario(BaseModel):
    test_script_name: str
    test_script_objective: str
    reason_to_test: str
    criticality_description: str
    criticality_score: int


class CreateScenariosResponse(BaseModel):
    ok: bool
    message: str
    scenarios: Optional[List[Scenario]] = None


class JiraDetails(BaseModel):
    jira_endpoint: str
    jira_api_token: str
    jira_username: str
    jira_id: str
    
class UserDescription(BaseModel):
    user_description: str
    
class ApiBuilderResponse(BaseModel):
    swagger_dictionary: dict
    
class DataAmplifierResponse(BaseModel):
    data: Optional[Dict] = None
    status: bool
    message: str
    
class AssertionHeaderRequest(BaseModel):
    headers: Union[List, Dict, str]
    
# class AssertionHeaderResponse(BaseModel):
#     assertions: Union[List, Dict, str]
class AssertionResponseRequest(BaseModel):
    response: Union[List, Dict, str]
    
    
class AssertionAllRequest(BaseModel):
    headers: Union[List, Dict, str]
    response: Union[List, Dict, str]