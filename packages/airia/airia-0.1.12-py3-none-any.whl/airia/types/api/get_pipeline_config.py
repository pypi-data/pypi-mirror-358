from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    id: str
    export_version: str = Field(alias="exportVersion")
    tagline: Optional[str] = None
    agent_description: Optional[str] = Field(alias="agentDescription", default=None)
    industry: Optional[str] = None
    tasks: Optional[str] = None
    credential_export_option: str = Field(alias="credentialExportOption")
    data_source_export_option: str = Field(alias="dataSourceExportOption")
    version_information: str = Field(alias="versionInformation")
    state: str


class Agent(BaseModel):
    name: str
    execution_name: str = Field(alias="executionName")
    agent_description: Optional[str] = Field(alias="agentDescription", default=None)
    video_link: Optional[str] = Field(alias="videoLink", default=None)
    industry: Optional[str] = None
    sub_industries: List[str] = Field(alias="subIndustries", default_factory=list)
    agent_details: Dict[str, Any] = Field(alias="agentDetails", default_factory=dict)
    id: str
    agent_icon: Optional[str] = Field(alias="agentIcon", default=None)
    steps: List[Dict[str, Any]]


class PromptMessage(BaseModel):
    text: str
    order: int


class Prompt(BaseModel):
    name: str
    version_change_description: str = Field(alias="versionChangeDescription")
    prompt_message_list: List[PromptMessage] = Field(alias="promptMessageList")
    id: str


class CredentialData(BaseModel):
    key: str
    value: str


class CredentialsDefinition(BaseModel):
    name: str
    credential_type: str = Field(alias="credentialType")
    source_type: str = Field(alias="sourceType")
    credential_data_list: List[CredentialData] = Field(alias="credentialDataList")
    id: str


class HeaderDefinition(BaseModel):
    key: str
    value: str


class ParameterDefinition(BaseModel):
    name: str
    parameter_type: str = Field(alias="parameterType")
    parameter_description: str = Field(alias="parameterDescription")
    default: str
    valid_options: List[str] = Field(alias="validOptions", default_factory=list)
    id: str


class Tool(BaseModel):
    tool_type: str = Field(alias="toolType")
    name: str
    standardized_name: str = Field(alias="standardizedName")
    tool_description: str = Field(alias="toolDescription")
    purpose: str
    api_endpoint: str = Field(alias="apiEndpoint")
    credentials_definition: Optional[CredentialsDefinition] = Field(
        alias="credentialsDefinition"
    )
    headers_definition: List[HeaderDefinition] = Field(alias="headersDefinition")
    body: str
    parameters_definition: List[ParameterDefinition] = Field(
        alias="parametersDefinition"
    )
    method_type: str = Field(alias="methodType")
    route_through_acc: bool = Field(alias="routeThroughACC")
    use_user_credentials: bool = Field(alias="useUserCredentials")
    use_user_credentials_type: str = Field(alias="useUserCredentialsType")
    id: str


class Model(BaseModel):
    id: str
    display_name: str = Field(alias="displayName")
    model_name: str = Field(alias="modelName")
    prompt_id: Optional[str] = Field(alias="promptId", default=None)
    system_prompt_definition: Optional[Any] = Field(
        alias="systemPromptDefinition", default=None
    )
    url: str
    input_type: str = Field(alias="inputType")
    provider: str
    credentials_definition: Optional[CredentialsDefinition] = Field(
        alias="credentialsDefinition"
    )
    deployment_type: str = Field(alias="deploymentType")
    source_type: str = Field(alias="sourceType")
    connection_string: Optional[str] = Field(alias="connectionString", default=None)
    container_name: Optional[str] = Field(alias="containerName", default=None)
    deployed_key: Optional[str] = Field(alias="deployedKey", default=None)
    deployed_url: Optional[str] = Field(alias="deployedUrl", default=None)
    state: Optional[str] = None
    uploaded_container_id: Optional[str] = Field(
        alias="uploadedContainerId", default=None
    )
    library_model_id: Optional[str] = Field(alias="libraryModelId")
    input_token_price: str = Field(alias="inputTokenPrice")
    output_token_price: str = Field(alias="outputTokenPrice")
    token_units: int = Field(alias="tokenUnits")
    has_tool_support: bool = Field(alias="hasToolSupport")
    allow_airia_credentials: bool = Field(alias="allowAiriaCredentials")
    allow_byok_credentials: bool = Field(alias="allowBYOKCredentials")
    author: Optional[str]
    price_type: str = Field(alias="priceType")


class PythonCodeBlock(BaseModel):
    id: str
    code: str


class Router(BaseModel):
    id: str
    model_id: str = Field(alias="modelId")
    model: Optional[Any] = None
    router_config: Dict[str, Dict[str, Any]] = Field(alias="routerConfig")


class ChunkingConfig(BaseModel):
    id: str
    chunk_size: int = Field(alias="chunkSize")
    chunk_overlap: int = Field(alias="chunkOverlap")
    strategy_type: str = Field(alias="strategyType")


class DataSourceFile(BaseModel):
    data_source_id: str = Field(alias="dataSourceId")
    file_path: Optional[str] = Field(None, alias="filePath")
    input_token: Optional[str] = Field(None, alias="inputToken")
    file_count: Optional[int] = Field(None, alias="fileCount")


class DataSource(BaseModel):
    id: str = Field(alias="id")
    name: Optional[str] = None
    execution_name: Optional[str] = Field(None, alias="executionName")
    chunking_config: ChunkingConfig = Field(alias="chunkingConfig")
    data_source_type: str = Field(alias="dataSourceType")
    database_type: str = Field(alias="databaseType")
    embedding_provider: str = Field(alias="embeddingProvider")
    is_user_specific: bool = Field(alias="isUserSpecific")
    files: Optional[List[DataSourceFile]] = None
    configuration_json: Optional[str] = Field(None, alias="configurationJson")
    credentials: Optional[CredentialsDefinition]
    is_image_processing_enabled: bool = Field(alias="isImageProcessingEnabled")


class GetPipelineConfigResponse(BaseModel):
    metadata: Metadata
    agent: Agent
    data_sources: Optional[List[DataSource]] = Field(
        alias="dataSources", default_factory=list
    )
    prompts: Optional[List[Prompt]] = Field(default_factory=list)
    tools: Optional[List[Tool]] = Field(default_factory=list)
    models: Optional[List[Model]] = Field(default_factory=list)
    memories: Optional[Any] = None
    python_code_blocks: Optional[List[PythonCodeBlock]] = Field(
        alias="pythonCodeBlocks", default_factory=list
    )
    routers: Optional[List[Router]] = Field(default_factory=list)
    deployment: Optional[Any] = None
