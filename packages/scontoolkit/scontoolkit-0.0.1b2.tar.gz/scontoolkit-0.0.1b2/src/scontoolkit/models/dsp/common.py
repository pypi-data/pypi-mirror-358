from pydantic import BaseModel, Field, HttpUrl
from typing import List, Literal, Optional, Any


class Auth(BaseModel):
    protocol: str
    version: str
    profile: Optional[List]

class Version(BaseModel):
    binding: Literal["HTTPS"]
    path: str
    version: Any
    auth: Optional[Auth] = None
    identifierType: Optional[str] = None
    serviceId: Optional[str] = None

class VersionResponse(BaseModel):
    protocolVersions: List[Version]

class DiDService(BaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"], Literal["https://www.w3.org/ns/did/v1"]] = Field(alias="@context")
    type: Literal["DataService", "CatalogService"]
    id: str
    serviceEndpoint: HttpUrl
#
#
#
# class SelfDescriptionResponse(BaseModel):
#     model_config = ConfigDict(populate_by_name=True)
#
#     context: Literal["https://w3id.org/dspace/2024/1/context.json"] = Field(
#         alias="@context"
#     )
#     type: Literal["ConnectorDescription"] = Field(alias="@type")
#     id: HttpUrl = Field(alias="@id")
#
#     title: str
#     description: str
#     version: str
#     securityProfile: HttpUrl
#     maintainer: HttpUrl