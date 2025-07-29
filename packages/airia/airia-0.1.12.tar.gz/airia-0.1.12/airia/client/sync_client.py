from typing import Any, Dict, List, Literal, Optional, overload

import loguru
import requests

from ..constants import (
    DEFAULT_ANTHROPIC_GATEWAY_URL,
    DEFAULT_BASE_URL,
    DEFAULT_OPENAI_GATEWAY_URL,
    DEFAULT_TIMEOUT,
)
from ..exceptions import AiriaAPIError
from ..types._api_version import ApiVersion
from ..types._request_data import RequestData
from ..types.api import (
    CreateConversationResponse,
    GetPipelineConfigResponse,
    PipelineExecutionDebugResponse,
    PipelineExecutionResponse,
    PipelineExecutionStreamedResponse,
    ProjectItem,
)
from ..utils.sse_parser import parse_sse_stream_chunked
from .base_client import AiriaBaseClient


class AiriaClient(AiriaBaseClient):
    """Synchronous client for interacting with the Airia API."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        log_requests: bool = False,
        custom_logger: Optional["loguru.Logger"] = None,
    ):
        """
        Initialize the synchronous Airia API client.

        Args:
            base_url: Base URL of the Airia API.
            api_key: API key for authentication. If not provided, will attempt to use AIRIA_API_KEY environment variable.
            bearer_token: Bearer token for authentication. Must be provided explicitly (no environment variable fallback).
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
        """
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            bearer_token=bearer_token,
            timeout=timeout,
            log_requests=log_requests,
            custom_logger=custom_logger,
        )

        # Initialize session for synchronous requests
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    @classmethod
    def with_openai_gateway(
        cls,
        base_url: str = DEFAULT_BASE_URL,
        gateway_url: str = DEFAULT_OPENAI_GATEWAY_URL,
        api_key: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        log_requests: bool = False,
        custom_logger: Optional["loguru.Logger"] = None,
        **kwargs,
    ):
        """
        Initialize the synchronous Airia API client with OpenAI gateway capabilities.

        Args:
            base_url: Base URL of the Airia API.
            gateway_url: Base URL of the Airia Gateway API.
            api_key: API key for authentication. If not provided, will attempt to use AIRIA_API_KEY environment variable.
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
            **kwargs: Additional keyword arguments to pass to the OpenAI client initialization.
        """
        from openai import OpenAI

        client = cls(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            log_requests=log_requests,
            custom_logger=custom_logger,
        )
        cls.openai = OpenAI(
            api_key=client.api_key,
            base_url=gateway_url,
            **kwargs,
        )

        return client

    @classmethod
    def with_anthropic_gateway(
        cls,
        base_url: str = DEFAULT_BASE_URL,
        gateway_url: str = DEFAULT_ANTHROPIC_GATEWAY_URL,
        api_key: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        log_requests: bool = False,
        custom_logger: Optional["loguru.Logger"] = None,
        **kwargs,
    ):
        """
        Initialize the synchronous Airia API client with Anthropic gateway capabilities.

        Args:
            base_url: Base URL of the Airia API.
            gateway_url: Base URL of the Airia Gateway API.
            api_key: API key for authentication. If not provided, will attempt to use AIRIA_API_KEY environment variable.
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
            **kwargs: Additional keyword arguments to pass to the Anthropic client initialization.
        """
        from anthropic import Anthropic

        client = cls(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            log_requests=log_requests,
            custom_logger=custom_logger,
        )
        cls.anthropic = Anthropic(
            api_key=client.api_key,
            base_url=gateway_url,
            **kwargs,
        )

        return client

    @classmethod
    def with_bearer_token(
        cls,
        bearer_token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        log_requests: bool = False,
        custom_logger: Optional["loguru.Logger"] = None,
    ):
        """
        Initialize the synchronous Airia API client with bearer token authentication.

        Args:
            bearer_token: Bearer token for authentication.
            base_url: Base URL of the Airia API.
            timeout: Request timeout in seconds.
            log_requests: Whether to log API requests and responses. Default is False.
            custom_logger: Optional custom logger object to use for logging. If not provided, will use a default logger when `log_requests` is True.
        """
        return cls(
            base_url=base_url,
            bearer_token=bearer_token,
            timeout=timeout,
            log_requests=log_requests,
            custom_logger=custom_logger,
        )

    def _handle_exception(self, e: requests.HTTPError, url: str, correlation_id: str):
        # Log the error response if enabled
        if self.log_requests:
            self.logger.error(
                f"API Error: {e.response.status_code} {e.response.reason}\n"
                f"URL: {url}\n"
                f"Correlation ID: {correlation_id}"
            )

        # Extract error details from response if possible
        error_message = "API request failed"
        try:
            error_data = e.response.json()
            if isinstance(error_data, dict) and "message" in error_data:
                error_message = error_data["message"]
            elif isinstance(error_data, dict) and "error" in error_data:
                error_message = error_data["error"]
        except (ValueError, KeyError):
            # If JSON parsing fails or expected keys are missing
            error_message = f"API request failed: {str(e)}"

        # Make sure sensitive auth information is not included in error messages
        sanitized_message = error_message
        if self.api_key and self.api_key in sanitized_message:
            sanitized_message = sanitized_message.replace(self.api_key, "[REDACTED]")
        if self.bearer_token and self.bearer_token in sanitized_message:
            sanitized_message = sanitized_message.replace(
                self.bearer_token, "[REDACTED]"
            )

        # Raise custom exception with status code and sanitized message
        raise AiriaAPIError(
            status_code=e.response.status_code, message=sanitized_message
        ) from e

    def _make_request(self, method: str, request_data: RequestData) -> Dict[str, Any]:
        """
        Makes a synchronous HTTP request to the Airia API.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST')
            request_data: A dictionary containing the following request information:
                - url: The endpoint URL for the request
                - headers: HTTP headers to include in the request
                - payload: The JSON payload/body for the request
                - correlation_id: Unique identifier for request tracing

        Returns:
            resp (Dict[str, Any]): The JSON response from the API as a dictionary.

        Raises:
            AiriaAPIError: If the API returns an error response, with details about the error
            requests.HTTPError: For HTTP-related errors

        Note:
            This is an internal method used by other client methods to make API requests.
            It handles logging, error handling, and API key redaction in error messages.
        """
        try:
            # Make the request
            response = self.session.request(
                method=method,
                url=request_data.url,
                json=request_data.payload,
                params=request_data.params,
                headers=request_data.headers,
                timeout=self.timeout,
            )

            # Log the response if enabled
            if self.log_requests:
                self.logger.info(
                    f"API Response: {response.status_code} {response.reason}\n"
                    f"URL: {request_data.url}\n"
                    f"Correlation ID: {request_data.correlation_id}\n"
                )

            # Check for HTTP errors
            response.raise_for_status()

            # Returns the JSON response
            return response.json()

        except requests.HTTPError as e:
            self._handle_exception(e, request_data.url, request_data.correlation_id)

    def _make_request_stream(self, method: str, request_data: RequestData):
        """
        Makes a synchronous HTTP request to the Airia API.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST')
            request_data: A dictionary containing the following request information:
                - url: The endpoint URL for the request
                - headers: HTTP headers to include in the request
                - payload: The JSON payload/body for the request
                - correlation_id: Unique identifier for request tracing
            stream (bool): If True, the response will be streamed instead of downloaded all at once

        Yields:
            resp (Iterator[str]): Yields chunks of the response as they are received.

        Raises:
            AiriaAPIError: If the API returns an error response, with details about the error
            requests.HTTPError: For HTTP-related errors

        Note:
            This is an internal method used by other client methods to make API requests.
            It handles logging, error handling, and API key redaction in error messages.
        """
        try:
            # Make the request
            response = self.session.request(
                method=method,
                url=request_data.url,
                params=request_data.params,
                json=request_data.payload,
                headers=request_data.headers,
                timeout=self.timeout,
                stream=True,
            )

            # Log the response if enabled
            if self.log_requests:
                self.logger.info(
                    f"API Response: {response.status_code} {response.reason}\n"
                    f"URL: {request_data.url}\n"
                    f"Correlation ID: {request_data.correlation_id}\n"
                )

            # Check for HTTP errors
            response.raise_for_status()

            # Yields the response content as a stream
            for message in parse_sse_stream_chunked(response.iter_content()):
                yield message

        except requests.HTTPError as e:
            self._handle_exception(e, request_data.url, request_data.correlation_id)

    @overload
    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: Literal[False] = False,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: Literal[False] = False,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> PipelineExecutionResponse: ...

    @overload
    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: Literal[True] = True,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: Literal[False] = False,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> PipelineExecutionDebugResponse: ...

    @overload
    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: bool = False,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: Literal[True] = True,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> PipelineExecutionStreamedResponse: ...

    def execute_pipeline(
        self,
        pipeline_id: str,
        user_input: str,
        debug: bool = False,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        async_output: bool = False,
        include_tools_response: bool = False,
        images: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        data_source_folders: Optional[Dict[str, Any]] = None,
        data_source_files: Optional[Dict[str, Any]] = None,
        in_memory_messages: Optional[List[Dict[str, str]]] = None,
        current_date_time: Optional[str] = None,
        save_history: bool = True,
        additional_info: Optional[List[Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """
        Execute a pipeline with the provided input.

        Args:
            pipeline_id: The ID of the pipeline to execute.
            user_input: input text to process.
            debug: Whether debug mode execution is enabled. Default is False.
            user_id: Optional ID of the user making the request (guid).
            conversation_id: Optional conversation ID (guid).
            async_output: Whether to stream the response. Default is False.
            include_tools_response: Whether to return the initial LLM tool result. Default is False.
            images: Optional list of images formatted as base64 strings.
            files: Optional list of files formatted as base64 strings.
            data_source_folders: Optional data source folders information.
            data_source_files: Optional data source files information.
            in_memory_messages: Optional list of in-memory messages, each with a role and message.
            current_date_time: Optional current date and time in ISO format.
            save_history: Whether to save the userInput and output to conversation history. Default is True.
            additional_info: Optional additional information.
            prompt_variables: Optional variables to be used in the prompt.
            correlation_id: Optional correlation ID for request tracing. If not provided,
                        one will be generated automatically.

        Returns:
            The API response as a dictionary.

        Raises:
            AiriaAPIError: If the API request fails with details about the error.
            requests.RequestException: For other request-related errors.

        Example:
            >>> client = AiriaClient(api_key="your_api_key")
            >>> response = client.execute_pipeline(
            ...     pipeline_id="pipeline_123",
            ...     user_input="Tell me about quantum computing"
            ... )
            >>> print(response.result)
        """
        request_data = self._pre_execute_pipeline(
            pipeline_id=pipeline_id,
            user_input=user_input,
            debug=debug,
            user_id=user_id,
            conversation_id=conversation_id,
            async_output=async_output,
            include_tools_response=include_tools_response,
            images=images,
            files=files,
            data_source_folders=data_source_folders,
            data_source_files=data_source_files,
            in_memory_messages=in_memory_messages,
            current_date_time=current_date_time,
            save_history=save_history,
            additional_info=additional_info,
            prompt_variables=prompt_variables,
            correlation_id=correlation_id,
            api_version=ApiVersion.V2.value,
        )
        resp = (
            self._make_request_stream("POST", request_data)
            if async_output
            else self._make_request("POST", request_data)
        )

        if not async_output:
            if not debug:
                return PipelineExecutionResponse(**resp)
            return PipelineExecutionDebugResponse(**resp)

        return PipelineExecutionStreamedResponse(stream=resp)

    def get_projects(self, correlation_id: Optional[str] = None) -> List[ProjectItem]:
        """
        Retrieve a list of all projects accessible to the authenticated user.

        This method fetches comprehensive information about all projects that the
        current user has access to, including project metadata, creation details,
        and status information.

        Args:
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            List[ProjectItem]: A list of ProjectItem objects containing project
                information. Returns an empty list if no projects are accessible
                or found.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaClient

            client = AiriaClient(api_key="your_api_key")

            # Get all accessible projects
            projects = client.get_projects()

            for project in projects:
                print(f"Project: {project.name}")
                print(f"ID: {project.id}")
                print(f"Description: {project.description}")
                print(f"Created: {project.created_at}")
                print("---")
            ```

        Note:
            The returned projects are filtered based on the authenticated user's
            permissions. Users will only see projects they have been granted
            access to.
        """
        request_data = self._pre_get_projects(
            correlation_id=correlation_id, api_version=ApiVersion.V1.value
        )
        resp = self._make_request("GET", request_data)

        if "items" not in resp or len(resp["items"]) == 0:
            return []

        return [ProjectItem(**item) for item in resp["items"]]

    def get_active_pipelines_ids(
        self, project_id: Optional[str] = None, correlation_id: Optional[str] = None
    ) -> List[str]:
        """
        Retrieve a list of active pipeline IDs.

        This method fetches the IDs of all active pipelines, optionally filtered by project.
        Active pipelines are those that are currently deployed and available for execution.

        Args:
            project_id (str, optional): The unique identifier of the project to filter
                pipelines by. If not provided, returns active pipelines from all projects
                accessible to the authenticated user.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            List[str]: A list of pipeline IDs that are currently active. Returns an
                empty list if no active pipelines are found.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The project_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaClient

            client = AiriaClient(api_key="your_api_key")

            # Get all active pipeline IDs
            pipeline_ids = client.get_active_pipelines_ids()
            print(f"Found {len(pipeline_ids)} active pipelines")

            # Get active pipeline IDs for a specific project
            project_pipelines = client.get_active_pipelines_ids(
                project_id="your_project_id"
            )
            print(f"Project has {len(project_pipelines)} active pipelines")
            ```

        Note:
            Only pipelines with active versions are returned. Inactive or archived
            pipelines are not included in the results.
        """
        request_data = self._pre_get_active_pipelines_ids(
            project_id=project_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = self._make_request("GET", request_data)

        if "items" not in resp or len(resp["items"]) == 0:
            return []

        pipeline_ids = [r["activeVersion"]["pipelineId"] for r in resp["items"]]

        return pipeline_ids

    def get_pipeline_config(
        self, pipeline_id: str, correlation_id: Optional[str] = None
    ) -> GetPipelineConfigResponse:
        """
        Retrieve configuration details for a specific pipeline.

        This method fetches comprehensive information about a pipeline including its
        deployment details, execution statistics, version information, and metadata.

        Args:
            pipeline_id (str): The unique identifier of the pipeline to retrieve
                configuration for.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            GetPipelineConfigResponse: A response object containing the pipeline
                configuration.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The pipeline_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaClient

            client = AiriaClient(api_key="your_api_key")

            # Get pipeline configuration
            config = client.get_pipeline_config(
                pipeline_id="your_pipeline_id"
            )

            print(f"Pipeline: {config.deployment_name}")
            print(f"Description: {config.deployment_description}")
            print(f"Success rate: {config.execution_stats.success_count}")
            print(f"Active version: {config.active_version.version_number}")
            ```

        Note:
            This method only retrieves configuration information and does not
            execute the pipeline. Use execute_pipeline() to run the pipeline.
        """
        request_data = self._pre_get_pipeline_config(
            pipeline_id=pipeline_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = self._make_request("GET", request_data)

        return GetPipelineConfigResponse(**resp)

    def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None,
        deployment_id: Optional[str] = None,
        data_source_files: Dict[str, Any] = {},
        is_bookmarked: bool = False,
        correlation_id: Optional[str] = None,
    ) -> CreateConversationResponse:
        """
        Create a new conversation.

        Args:
            user_id (str): The unique identifier of the user creating the conversation.
            title (str, optional): The title for the conversation. If not provided,
                the conversation will be created without a title.
            deployment_id (str, optional): The unique identifier of the deployment
                to associate with the conversation. If not provided, the conversation
                will not be associated with any specific deployment.
            data_source_files (dict): Configuration for data source files
                to be associated with the conversation. If not provided, no data
                source files will be associated.
            is_bookmarked (bool): Whether the conversation should be bookmarked.
                Defaults to False.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            CreateConversationResponse: A response object containing the created
                conversation details including its ID, creation timestamp, and
                all provided parameters.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The user_id doesn't exist (404)
                - The deployment_id is invalid (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaClient

            client = AiriaClient(api_key="your_api_key")

            # Create a basic conversation
            conversation = client.create_conversation(
                user_id="user_123"
            )
            print(f"Created conversation: {conversation.id}")

            # Create a conversation with all options
            conversation = client.create_conversation(
                user_id="user_123",
                title="My Research Session",
                deployment_id="deployment_456",
                data_source_files={"documents": ["doc1.pdf", "doc2.txt"]},
                is_bookmarked=True
            )
            print(f"Created bookmarked conversation: {conversation.id}")
            ```

        Note:
            The user_id is required and must correspond to a valid user in the system.
            All other parameters are optional and can be set to None or their default values.
        """
        request_data = self._pre_create_conversation(
            user_id=user_id,
            title=title,
            deployment_id=deployment_id,
            data_source_files=data_source_files,
            is_bookmarked=is_bookmarked,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = self._make_request("POST", request_data)

        return CreateConversationResponse(**resp)
