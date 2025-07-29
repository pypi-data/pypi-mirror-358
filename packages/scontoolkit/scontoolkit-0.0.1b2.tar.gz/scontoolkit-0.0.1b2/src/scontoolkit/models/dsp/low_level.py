from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union, ForwardRef

# Forward references
DatasetRef = ForwardRef("Dataset")
DataServiceRef = ForwardRef("DataService")


class Action(BaseModel): str

class Constraint(BaseModel):
    leftOperand: str
    operator: str
    rightOperand: str

class Duty(BaseModel):
    action: Optional[Action]
    constraint: Optional[List[Constraint]]

class Rule(BaseModel):
    action: Action
    constraint: Optional[List[Constraint]]
    duty: Optional[List[Duty]]

class Agreement(BaseModel):
    id: str = Field(alias='@id')
    type: Literal["Agreement"] = Field(alias='@type')
    assignee: str
    assigner: str
    target: str
    obligation: Optional[List[Duty]]
    permission: Optional[List[Rule]]
    profile: Optional[List[str]]
    prohibition: Optional[List[Rule]]
    timestamp: Optional[str]

class Offer(BaseModel):
    id: str = Field(alias='@id')
    type: Optional[Literal["Offer"]] = Field(alias='@type')
    obligation: Optional[List[Duty]]
    permission: Optional[List[Rule]]
    profile: Optional[List[str]]
    prohibition: Optional[List[Rule]]


class Distribution(BaseModel):
    accessService: Union[DataServiceRef, str]
    format: str
    hasPolicy: Optional[List[Offer]]

class Dataset(BaseModel):
    id: str = Field(alias='@id')
    distribution: List[Distribution]
    hasPolicy: List[Offer]

class DataService(BaseModel):
    id: str = Field(alias='@id')
    type: Optional[Literal["DataService"]] = Field(alias='@type')
    endpointURL: Optional[str]
    servesDataset: Optional[List[DatasetRef]]

class Catalog(BaseModel):
    id: str = Field(alias='@id')
    type: Literal["Catalog"] = Field(alias='@type')
    catalog: Optional[List["Catalog"]]  # Recursive self-reference
    dataset: Optional[List[Dataset]]
    service: Optional[List[DataService]]

class EndpointProperty(BaseModel):
    type: Literal["EndpointProperty"] = Field(alias='@type')
    name: str
    value: str

class DataAddress(BaseModel):
    type: Literal["DataAddress"] = Field(alias='@type')
    endpointType: str
    endpoint: Optional[str]
    endpointProperties: Optional[List[EndpointProperty]]

class MessageOffer(Offer):
    target: Optional[str]

Distribution.model_rebuild()
DataService.model_rebuild()
Catalog.model_rebuild()
