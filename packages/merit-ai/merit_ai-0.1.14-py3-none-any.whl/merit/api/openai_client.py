"""
OpenAI API Client for MERIT

This module provides a client for the OpenAI API that properly implements
the AIAPIClient interface with full MERIT system integration.
"""

import os
from typing import Dict, Any, List, Optional, Union, Tuple
from dotenv import load_dotenv

from openai import OpenAI as SDKOpenAIClient, AzureOpenAI as SDKAzureOpenAIClient, APIError, AuthenticationError, RateLimitError, APIConnectionError, APITimeoutError, BadRequestError # Other errors can be added as needed

from .client import AIAPIClient, AIAPIClientConfig # Import both parent class and its config
from .run_config import RetryConfig, with_retry, adaptive_throttle # Import decorators
from ..core.logging import get_logger
import json # For safe logging of RetryConfig
from ..core.utils import parse_json # May still be needed for prompts, but not for SDK response parsing
from .client import get_api_key # Import for resolving API key from .client
from .errors import (
    MeritAPIAuthenticationError,
    MeritAPIConnectionError,
    MeritAPIServerError,
    MeritAPITimeoutError,
    MeritAPIRateLimitError,
    MeritAPIResourceNotFoundError,
    MeritAPIInvalidRequestError
)

logger = get_logger(__name__)

# Default base URL for OpenAI API (SDK handles this, but good for reference or overrides)
OPENAI_DEFAULT_BASE_URL = "https://api.openai.com/v1"

# from merit.api.client passed by create_ai_client, or direct parameters.

class OpenAIClientConfig(AIAPIClientConfig):
    """
    Configuration specific to the OpenAI client, using the OpenAI SDK.
    Inherits from the generic AIAPIClientConfig.
    
    For Azure OpenAI:
    - Set api_type to 'azure'
    - Set api_version (required for Azure)
    - Set base_url to your Azure endpoint URL
    - Provide api_key (your Azure OpenAI API key)
    """
    embedding_model: str = "text-embedding-ada-002"
    organization_id: Optional[str] = None
    # SDK specific parameters, can override defaults in OpenAIClient.__init__
    request_timeout: Optional[Union[float, Tuple[float, float]]] = 60.0 
    max_sdk_retries: Optional[int] = 2
    api_type: str = "openai"  # Can be 'openai' or 'azure'
    api_version: Optional[str] = None  # Required for api_type 'azure'

    def __init__(
        self,
        # Fields from generic AIAPIClientConfig that we want to be explicit about or default differently
        provider: str = "openai", # Default provider for this config
        api_key: Optional[str] = None,
        api_key_env_var: Optional[str] = None,
        base_url: Optional[str] = OPENAI_DEFAULT_BASE_URL, 
        model: Optional[str] = "gpt-4o-mini", 
        strict: bool = False,
        # Generic retry/throttling params from BaseAPIClientConfig, passed to super()
        enable_retries: bool = True,
        enable_throttling: bool = True,
        max_retries: int = 3, # Generic retry count for non-SDK logic if any, or for reference
        backoff_factor: float = 0.5,
        initial_delay: float = 0.5,
        min_delay: float = 0.05,
        max_delay: float = 2.0,
        # OpenAI-specific fields for this config class
        embedding_model: str = "text-embedding-ada-002",
        organization_id: Optional[str] = None,
        request_timeout: Optional[Union[float, Tuple[float, float]]] = 60.0,
        max_sdk_retries: Optional[int] = 2,
        retry_config: Optional[RetryConfig] = None, # Add retry_config parameter
        api_type: str = "openai",
        api_version: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            provider=provider,
            api_key=api_key,
            api_key_env_var=api_key_env_var,
            base_url=base_url,
            model=model,
            strict=strict,
            enable_retries=enable_retries,
            enable_throttling=enable_throttling,
            max_retries=max_retries, 
            backoff_factor=backoff_factor,
            initial_delay=initial_delay,
            min_delay=min_delay,
            max_delay=max_delay,
            retry_config=retry_config, # Pass retry_config to parent
            **kwargs # Pass remaining kwargs to parent
        )
        # Set OpenAI-specific attributes from parameters
        self.embedding_model = embedding_model
        self.organization_id = organization_id
        self.request_timeout = request_timeout
        self.max_sdk_retries = max_sdk_retries
        self.retry_config = retry_config # Store retry_config on the instance
        self.api_type = api_type
        self.api_version = api_version
        
        # Validate Azure configuration
        if self.api_type == "azure" and not self.api_version:
            logger.warning("api_version must be set when api_type is 'azure'. Azure OpenAI client will fail to initialize.")

class OpenAIClient(AIAPIClient):
    """
    OpenAI API client implementation using the official OpenAI Python SDK.
    
    This class provides methods to interact with the OpenAI API for tasks such as
    text generation and embeddings.
    """
    
    def __init__(self, config: OpenAIClientConfig):
        """
        Initialize the OpenAI client using an OpenAIClientConfig object.
        
        Args:
            config: An OpenAIClientConfig instance containing all necessary configurations.
        """
        # Store the config object for later use - CRITICAL: This must be set before anything else
        # as other methods rely on self.config being available
        self.config = config
        
        # Resolve API key using get_api_key which handles direct key and env var
        # Note: get_api_key expects a config object that has .api_key and .api_key_env_var
        # OpenAIClientConfig inherits these from AIAPIClientConfig.
        resolved_api_key = get_api_key(config) # Assuming get_api_key is accessible or moved/re-imported
        if not resolved_api_key:
            raise MeritAPIAuthenticationError("OpenAI API key could not be resolved from config.")

        super().__init__(
            api_key=resolved_api_key,
            base_url=config.base_url,
            model=config.model,
            strict=config.strict
            # Pass other relevant base parameters if BaseAPIClient.__init__ expects more
        )

        # Common arguments for both OpenAI and Azure OpenAI clients
        common_args = {
            "api_key": self.api_key,
            "timeout": config.request_timeout,
            "max_retries": config.max_sdk_retries 
        }
        
        # Add organization ID only if provided
        if config.organization_id:
            common_args["organization"] = config.organization_id

        # Initialize the appropriate client based on api_type
        if config.api_type == "azure":
            # Validate Azure-specific requirements
            if not config.api_version:
                error_msg = "api_version must be set when api_type is 'azure'"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            if not self.base_url:
                error_msg = "base_url (Azure endpoint) must be set when api_type is 'azure'"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            if self.base_url == OPENAI_DEFAULT_BASE_URL:
                error_msg = "base_url must be your Azure endpoint URL, not the default OpenAI URL"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Initialize Azure OpenAI client
            logger.info(f"Initializing AzureOpenAI client with endpoint: {self.base_url} and API version: {config.api_version}")
            self.sdk_client = SDKAzureOpenAIClient(
                azure_endpoint=self.base_url,
                api_version=config.api_version,
                **common_args
            )
        else:
            # Initialize standard OpenAI client
            logger.info(f"Initializing OpenAI client with base_url: {self.base_url}")
            self.sdk_client = SDKOpenAIClient(
                base_url=self.base_url,
                **common_args
            )
        
        # self.model is already set by super().__init__ if BaseAPIClient handles it
        # If not, it's set from config.model by super() or needs to be self.model = config.model here.
        # Assuming BaseAPIClient.__init__ sets self.model.
        self.embedding_model = config.embedding_model
        
        logger.info(f"Initialized OpenAIClient with SDK using OpenAIClientConfig. Model: {self.model}, Embedding Model: {self.embedding_model}")

        # DISABLED: Run configuration and retry mechanisms are completely disabled
        logger.info("Run configuration and retry mechanisms are disabled for OpenAIClient")
        self.retry_config = None
        # No retry decorators will be applied
    
    def _apply_retry_decorators(self):
        """
        Apply retry decorators to API methods after initialization is complete.
        This is called at the end of __init__ to ensure methods are fully defined before wrapping.
        """
        if not self.retry_config:
            logger.warning("No retry configuration available, skipping decorator application")
            return
            
        rc = self.retry_config
        
        try:
            # Wrap generate_text
            if hasattr(self, 'generate_text'):
                _original_generate_text = self.generate_text
                self.generate_text = adaptive_throttle(
                    with_retry(
                        max_retries=rc.max_retries,
                        backoff_factor=rc.backoff_factor,
                        jitter=rc.jitter,
                        retry_on=rc.retry_on_exceptions,
                        retry_status_codes=rc.retry_status_codes
                    )(_original_generate_text)
                )
                logger.info("Applied retry decorators to generate_text method")
                
            # Wrap get_embeddings
            if hasattr(self, 'get_embeddings'):
                _original_get_embeddings = self.get_embeddings
                self.get_embeddings = adaptive_throttle(
                    with_retry(
                        max_retries=rc.max_retries,
                        backoff_factor=rc.backoff_factor,
                        jitter=rc.jitter,
                        retry_on=rc.retry_on_exceptions,
                        retry_status_codes=rc.retry_status_codes
                    )(_original_get_embeddings)
                )
                logger.info("Applied retry decorators to get_embeddings method")
                
            # Log successful application
            if hasattr(rc, 'model_dump'):
                try:
                    loggable_rc_dict = rc.model_dump()
                    if 'retry_on_exceptions' in loggable_rc_dict and isinstance(loggable_rc_dict['retry_on_exceptions'], list):
                        loggable_rc_dict['retry_on_exceptions'] = [exc.__name__ for exc in loggable_rc_dict['retry_on_exceptions']]
                    logger.info(f"Applied adaptive retry to OpenAIClient methods with effective config: {json.dumps(loggable_rc_dict, indent=2, default=str)}")
                except Exception as e:
                    logger.warning(f"Failed to log retry config details: {e}")
        except Exception as e:
            logger.error(f"Error applying retry decorators: {e}", exc_info=True)
            # Continue without decorators rather than failing
            
    @property
    def is_authenticated(self) -> bool:
        """
        Check if the client is authenticated.
        
        Returns:
            bool: True if the client has a valid API key, False otherwise.
        """
        return self.api_key is not None
    
    def login(self) -> bool:
        """
        OpenAI uses API key authentication, so login is not applicable.
        
        Returns:
            bool: True if API key is present, False otherwise.
        """
        return self.is_authenticated
    
    def get_token(self) -> Optional[str]:
        """
        Get the API key (token equivalent for OpenAI).
        
        Returns:
            Optional[str]: The API key, or None if not set.
        """
        return self.api_key
    
    # @cache_embeddings # Decorator might need review for SDK
    # @validate_embeddings_response # Decorator might need review for SDK
    def get_embeddings(self, texts: Union[str, List[str]], strict: Optional[bool] = None, **kwargs) -> List[List[float]]:
        """
        Get embeddings for the given texts using the OpenAI SDK.
        
        Args:
            texts: A string or list of strings to get embeddings for.
            strict: Optional. Override client's default strict mode. If True, errors are raised. If False, attempts to return default values (e.g., empty list of lists). If None, client's 'strict' attribute is used.
            **kwargs: Additional arguments to pass to the OpenAI SDK's embeddings.create method.
                      This can include 'model' to override self.embedding_model.
        
        Returns:
            List[List[float]]: A list of embeddings, where each embedding is a list of floats.
            Returns empty list of lists ([[]] * len(texts)) on error if not strict.

        Raises:
            MeritAPIAuthenticationError: If authentication fails.
            MeritAPITimeoutError: If the request times out.
            MeritAPIRateLimitError: If rate limits are exceeded.
            MeritAPIInvalidRequestError: For bad requests.
            MeritAPIServerError: For other server-side errors from OpenAI.
            MeritAPIConnectionError: For connection issues.
        """
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts: # Handle empty list input
            return []

        embedding_model_to_use = kwargs.pop("model", self.embedding_model)
        logger.info(f"[SDK] Getting embeddings for {len(texts)} texts using model {embedding_model_to_use}")

        try:
            print(f"[SDK OpenAIClient.get_embeddings] Calling SDK: model='{embedding_model_to_use}', num_texts={len(texts)}, other_kwargs={kwargs}") # DEBUG
            response = self.sdk_client.embeddings.create(
                model=embedding_model_to_use,
                input=texts,
                **kwargs # Pass through any other compatible args
            )

            if response.data and all(hasattr(embedding_obj, 'embedding') for embedding_obj in response.data):
                embeddings = [embedding_obj.embedding for embedding_obj in response.data]
                logger.info(f"[SDK] Successfully got embeddings for {len(texts)} texts.")
                # print(f"[SDK OpenAIClient.get_embeddings] Response (first embedding shape): {len(embeddings[0]) if embeddings else 'N/A'}") # DEBUG
                return embeddings
            else:
                logger.error(f"[SDK] OpenAI API response for embeddings missing expected content. Response: {response}")
                if strict or (strict is None and self.strict):
                    raise ValueError("OpenAI API embeddings response missing expected content.")
                return [[] for _ in texts] # Return list of empty lists matching input length on error

        except AuthenticationError as e:
            logger.error(f"[SDK] OpenAI Authentication Error (Embeddings): {e}")
            raise MeritAPIAuthenticationError(f"OpenAI API Key or Organization ID is invalid (Embeddings): {e}") from e
        except APITimeoutError as e:
            logger.error(f"[SDK] OpenAI Request Timeout (Embeddings): {e}")
            raise MeritAPITimeoutError(f"OpenAI API request timed out (Embeddings): {e}") from e
        except RateLimitError as e:
            logger.error(f"[SDK] OpenAI Rate Limit Exceeded (Embeddings): {e}")
            raise MeritAPIRateLimitError(f"OpenAI API rate limit exceeded (Embeddings): {e}") from e
        except BadRequestError as e:
            logger.error(f"[SDK] OpenAI Bad Request Error (Embeddings): {e}")
            raise MeritAPIInvalidRequestError(f"OpenAI API bad request (Embeddings): {e}") from e
        except APIConnectionError as e:
            logger.error(f"[SDK] OpenAI API Connection Error (Embeddings): {e}")
            raise MeritAPIConnectionError(f"Failed to connect to OpenAI API (Embeddings): {e}") from e
        except APIError as e:
            logger.error(f"[SDK] OpenAI API Error (Embeddings): {e}")
            raise MeritAPIServerError(f"OpenAI API returned an error (Embeddings): {e}") from e
        except Exception as e:
            logger.error(f"[SDK] Unexpected error in OpenAIClient.get_embeddings: {e}", exc_info=True)
            if strict or (strict is None and self.strict):
                 raise
            return [[] for _ in texts]

    def generate_text(self, prompt: str, strict: Optional[bool] = None, **kwargs) -> str:
        """
        Generate text based on the given prompt using the OpenAI SDK's chat completions.
        
        Args:
            prompt: The prompt to generate text from. (Used if 'messages' not in kwargs)
            strict: Optional. Override client's default strict mode. If True, errors are raised. If False, attempts to return default values (e.g., empty string). If None, client's 'strict' attribute is used.
            **kwargs: Additional arguments to pass to the OpenAI SDK's chat.completions.create method.
                      This can include 'messages', 'temperature', 'max_tokens', etc.
                      If 'messages' is provided, 'prompt' is ignored.
        
        Returns:
            str: The generated text content.
            
        Raises:
            MeritAPIAuthenticationError: If authentication fails.
            MeritAPITimeoutError: If the request times out.
            MeritAPIRateLimitError: If rate limits are exceeded.
            MeritAPIInvalidRequestError: For bad requests (e.g., invalid model).
            MeritAPIServerError: For other server-side errors from OpenAI.
            MeritAPIConnectionError: For connection issues.
        """
        logger.info(f"[SDK] OpenAIClient.generate_text called. Model: {self.model}")

        # Prepare messages for the SDK
        if "messages" in kwargs:
            messages = kwargs.pop("messages")
        else:
            messages = [{"role": "user", "content": prompt}]

        # Prepare other parameters for the SDK call, using defaults if not provided
        temperature = kwargs.pop("temperature", 0.7)
        max_tokens = kwargs.pop("max_tokens", 1000)
        
        params = {
            "model": self.model, # self.model should be the Azure deployment name if using Azure
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        # Add any remaining kwargs to params to be passed to the SDK
        params.update(kwargs)

        try:
            # Detailed logging for Azure debugging (only log at debug level to avoid exposing sensitive info)
            if self.config.api_type == "azure":
                logger.debug(f"Azure OpenAI call details:")
                logger.debug(f"  - Azure endpoint: {self.base_url}")
                logger.debug(f"  - API key provided: {bool(self.api_key)}")
                logger.debug(f"  - API version: {self.config.api_version}")
                logger.debug(f"  - Model/deployment name: {params.get('model')}")
                logger.debug(f"  - Temperature: {params.get('temperature')}")
                logger.debug(f"  - Max tokens: {params.get('max_tokens')}")

            # Simplified messages logging for brevity
            log_messages_str = str(params.get('messages', []))
            if len(log_messages_str) > 500:
                log_messages_str = log_messages_str[:250] + "... (truncated) ..." + log_messages_str[-250:]
        
            logger.info(f"[SDK OpenAIClient.generate_text] Calling SDK: model='{params.get('model')}', messages={log_messages_str}, temperature={params.get('temperature')}, max_tokens={params.get('max_tokens')}, other_kwargs={kwargs}")
        
            completion = self.sdk_client.chat.completions.create(**params)
        
            if completion.choices and completion.choices[0].message and completion.choices[0].message.content:
                generated_content = completion.choices[0].message.content
                logger.info(f"[SDK] Successfully generated text using model {params.get('model')}.")
                return generated_content
            else:
                logger.error(f"[SDK] OpenAI API response missing expected content. Response: {completion.model_dump_json(indent=2) if completion else 'None'}")
                if strict or (strict is None and self.strict):
                    raise ValueError("OpenAI API response missing expected content.")
                return ""

        except AuthenticationError as e:
            logger.error(f"[SDK] OpenAI Authentication Error: {e}")
            raise MeritAPIAuthenticationError(f"OpenAI API Key or Organization ID is invalid: {e}") from e
        except APITimeoutError as e:
            logger.error(f"[SDK] OpenAI Request Timeout: {e}")
            raise MeritAPITimeoutError(f"OpenAI API request timed out: {e}") from e
        except RateLimitError as e:
            logger.error(f"[SDK] OpenAI Rate Limit Exceeded: {e}")
            raise MeritAPIRateLimitError(f"OpenAI API rate limit exceeded: {e}") from e
        except BadRequestError as e: # Covers model not found, invalid requests
            logger.error(f"[SDK] OpenAI Bad Request Error (e.g., model not found, invalid params): {e}")
            # Check if it's a 404 and potentially a resource not found for Azure
            if e.response and e.response.status_code == 404:
                 raise MeritAPIResourceNotFoundError(f"OpenAI API resource not found (404): {e.response.text}") from e
            raise MeritAPIInvalidRequestError(f"OpenAI API bad request: {e}") from e
        except APIConnectionError as e:
            logger.error(f"[SDK] OpenAI API Connection Error: {e}")
            raise MeritAPIConnectionError(f"Failed to connect to OpenAI API: {e}") from e
        except APIError as e: # Catch-all for other OpenAI API errors (like server errors)
            logger.error(f"[SDK] OpenAI API Error: {e}")
            # Check if it's a 404 and potentially a resource not found for Azure (if not caught by BadRequestError)
            if e.response and e.response.status_code == 404:
                 raise MeritAPIResourceNotFoundError(f"OpenAI API resource not found (404): {e.response.text}") from e
            raise MeritAPIServerError(f"OpenAI API returned an error: {e}") from e
        except Exception as e: # Catch any other unexpected errors
            logger.error(f"[SDK] Unexpected error in OpenAIClient.generate_text: {e}", exc_info=True)
            if strict or (strict is None and self.strict):
                 raise
            return ""
    
    def create_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Create a chat completion with multiple messages.
        
        This is more flexible than generate_text() which only supports a single prompt.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the API.
            
        Returns:
            Dict[str, Any]: The complete API response.
        """
        # Set default parameters
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
        }
        
        # Update with any provided kwargs
        params.update(kwargs)
        
        try:
            logger.info(f"Creating chat completion with model {self.model}")
            
            # Use the SDK client for chat completions
            response = self.sdk_client.chat.completions.create(**params)
            return response.model_dump() # Convert the SDK response object to a dict
        
        except Exception as e:
            merit_error = self._convert_requests_error(e, "chat/completions")
            logger.error(f"Failed to create chat completion: {merit_error}")
            return {"error": str(merit_error)}
    
    def list_models(self) -> List[str]:
        """
        List available models from OpenAI.
        
        Returns:
            List[str]: List of model IDs.
        """
        try:
            logger.info("Listing available models")
            
            # Use the SDK client to list models
            response = self.sdk_client.models.list()
            return [model.id for model in response.data]
        
        except Exception as e:
            merit_error = self._convert_requests_error(e, "models")
            logger.error(f"Failed to list models: {merit_error}")
            return []
