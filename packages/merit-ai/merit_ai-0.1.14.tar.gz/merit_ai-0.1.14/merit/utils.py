import os
import importlib
from typing import Any, Union, List, Dict
import csv
import json
from pathlib import Path

from merit.knowledge.config import (
    KnowledgeBaseConfig as KnowledgeBaseConfigPydantic,
    KnowledgeBaseCsvConfig,
    KnowledgeBaseJsonConfig
)
from merit.api.client import AIAPIClient, AIAPIClientConfig # Added AIAPIClientConfig import
from merit.api.openai_client import OpenAIClient, OpenAIClientConfig as SpecificOpenAIClientConfig # Renamed to avoid confusion
from merit.api.gemini_client import GeminiClient
from merit.api.errors import MeritAPIAuthenticationError, MeritAPIInvalidRequestError
from merit.api.client import get_api_key # Import get_api_key from its new location

# Assuming merit.core.utils.parse_json exists or defining a simple one here
# If you have a robust parse_json in merit.core.utils, prefer that.
_parse_json_defined_locally = False
try:
    from merit.core.utils import parse_json
except ImportError:
    _parse_json_defined_locally = True
    def parse_json(json_string: str) -> Any:
        """Basic JSON parsing.
           Replace with merit.core.utils.parse_json if available.
        """
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            # Log or handle more gracefully if needed
            raise ValueError(f"Invalid JSON string: {e}") from e
    if _parse_json_defined_locally:
        print("Warning: merit.core.utils.parse_json not found. Using a basic local definition for parse_json in merit.utils.")

# --- AI Utils --- 

# get_api_key function has been moved to merit.api.client.py

def create_ai_client(config_obj: AIAPIClientConfig) -> AIAPIClient:
    """
    Factory function to create an AI client based on the provider specified in the AIAPIClientConfig object.
    """
    provider = config_obj.provider if hasattr(config_obj, 'provider') else None
    if not provider:
        # Attempt to infer provider if config_obj is a specific subclass like OpenAIClientConfig
        # This part might need more robust type checking or specific config classes for each provider
        if type(config_obj).__name__ == 'OpenAIClientConfig': # Assuming OpenAIClientConfig is imported
            provider = 'openai'
        elif type(config_obj).__name__ == 'GeminiClientConfig': # Assuming GeminiClientConfig is imported
            provider = 'google'
        else:
            raise MeritAPIInvalidRequestError("'provider' must be specified in AIAPIClientConfig or be inferable from its type.")

    model = config_obj.model if hasattr(config_obj, 'model') and config_obj.model else "gpt-4o-mini"
    api_key_resolved = None
    if provider != "custom":
        api_key_resolved = get_api_key(config_obj)

    if provider == "openai":
        # OpenAIClient constructor takes api_key and model directly.
        # It can also take a 'config' object of its own type (OpenAIClientConfig from openai_client.py)
        # which would then use its own internal logic to set api_key, model etc.
        # For simplicity here, we pass them directly if available on the generic AIAPIClientConfig.
        # Create the specific OpenAIClientConfig instance
        # Fields are taken from the generic config_obj (AIAPIClientConfig from client.py)
        # and any _additional_params it might hold for provider-specific settings.
        additional_params = getattr(config_obj, '_additional_params', {})

        openai_cfg = SpecificOpenAIClientConfig(
            # Provider is implicitly openai here
            api_key=api_key_resolved, # This is already resolved by get_api_key
            api_key_env_var=getattr(config_obj, 'api_key_env_var', None),
            base_url=getattr(config_obj, 'base_url', None), # Let OpenAIClientConfig apply its default if None
            model=model, # This is already resolved
            strict=getattr(config_obj, 'strict', False),
            
            # Pass through generic retry/throttling params from BaseAPIClientConfig part of AIAPIClientConfig
            enable_retries=getattr(config_obj, 'enable_retries', True),
            enable_throttling=getattr(config_obj, 'enable_throttling', True),
            max_retries=getattr(config_obj, 'max_retries', 3), # Generic retries
            backoff_factor=getattr(config_obj, 'backoff_factor', 0.5),
            initial_delay=getattr(config_obj, 'initial_delay', 0.5),
            min_delay=getattr(config_obj, 'min_delay', 0.05),
            max_delay=getattr(config_obj, 'max_delay', 2.0),

            # OpenAI-specific fields, potentially from _additional_params or direct attributes if AIAPIClientConfig was extended
            embedding_model=additional_params.get('embedding_model', getattr(config_obj, 'embedding_model', "text-embedding-ada-002")),
            organization_id=additional_params.get('organization_id', getattr(config_obj, 'organization_id', None)),
            request_timeout=additional_params.get('request_timeout', getattr(config_obj, 'request_timeout', 60.0)),
            max_sdk_retries=additional_params.get('max_sdk_retries', getattr(config_obj, 'max_sdk_retries', 2)),
            
            # Pass any other kwargs that might have been in _additional_params and are accepted by OpenAIClientConfig's __init__
            **{k: v for k, v in additional_params.items() if k not in ['embedding_model', 'organization_id', 'request_timeout', 'max_sdk_retries']}
        )
        return OpenAIClient(config=openai_cfg)
    
    elif provider == "google": 
        # Assuming GeminiClient also takes api_key and model similarly
        return GeminiClient(api_key=api_key_resolved, model=model)
    
    elif provider == "custom":
        # For custom, AIAPIClientConfig might not have custom_client_module/class
        # This logic might need to be revisited if we rely solely on AIAPIClientConfig
        # For now, assuming these might be in _additional_params of AIAPIClientConfig
        custom_module_path = getattr(config_obj, '_additional_params', {}).get("custom_client_module")
        custom_class_name = getattr(config_obj, '_additional_params', {}).get("custom_client_class")
        
        if not custom_module_path or not custom_class_name:
            raise MeritAPIInvalidRequestError(
                "'custom_client_module' and 'custom_client_class' must be specified for 'custom' AI provider (e.g., in kwargs of AIAPIClientConfig)."
            )
        try:
            module = importlib.import_module(custom_module_path)
            client_class = getattr(module, custom_class_name)
            if not issubclass(client_class, AIAPIClient):
                print(f"Warning: Custom client {custom_class_name} does not inherit from AIAPIClient.")
            
            # Pass attributes from AIAPIClientConfig and any additional_params
            init_kwargs = {k: v for k, v in vars(config_obj).items() if not k.startswith('_') and k not in ['provider']} # Exclude 'provider' as it's handled
            init_kwargs.update(getattr(config_obj, '_additional_params', {}))
            if api_key_resolved and 'api_key' not in init_kwargs:
                 init_kwargs['api_key'] = api_key_resolved
            if 'model' not in init_kwargs:
                init_kwargs['model'] = model
            return client_class(**init_kwargs)
        except ImportError:
            raise MeritAPIInvalidRequestError(f"Could not import custom client module: {custom_module_path}")
        except AttributeError:
            raise MeritAPIInvalidRequestError(f"Could not find class {custom_class_name} in module {custom_module_path}")
        except Exception as e:
            raise MeritAPIInvalidRequestError(f"Error initializing custom client {custom_class_name}: {e}")
    else:
        raise NotImplementedError(f"AI provider '{provider}' is not yet supported.")

# --- System Client Utils ---

def create_system_client(config_obj: 'SystemClientConfig') -> 'BaseSystemClient': # type: ignore
    """
    Factory function to create a System Client based on the configuration object.
    """
    # Imports are inside the function to avoid circular dependencies if utils.py is imported by config.models or system clients
    from merit.config.models import SystemClientHttpConfig, SystemClientPythonModuleConfig, SystemClientConfig # Ensure SystemClientConfig is available for type hint resolution
    from merit.core.base_models import BaseSystemClient # For return type hint
    from merit.core.system_clients import HttpSystemClient, PythonModuleSystemClient

    if isinstance(config_obj, SystemClientHttpConfig):
        return HttpSystemClient(config=config_obj)
    elif isinstance(config_obj, SystemClientPythonModuleConfig):
        return PythonModuleSystemClient(config=config_obj)
    # Add other client types here, e.g., SystemClientCurlConfig if it has a dedicated client class
    # elif isinstance(config_obj, SystemClientCurlConfig):
    #     # Ensure CurlSystemClient is imported from merit.core.system_clients if defined there
    #     return CurlSystemClient(config=config_obj) # Assuming CurlSystemClient exists
    else:
        client_type = getattr(config_obj, 'type', 'unknown')
        raise NotImplementedError(f"System client type '{client_type}' derived from config_obj '{type(config_obj).__name__}' is not yet supported by create_system_client.")

# --- Config Loading Utils ---

CONFIG_VARIABLE_NAME = "config" # Default, can be overridden by importing from merit.cli if preferred

def load_config_from_file(config_path_str: str) -> 'MeritMainConfig': # type: ignore
    """Loads the MERIT configuration from a Python file."""
    # Imports needed for this function
    from pathlib import Path
    import sys
    import importlib.util
    import inspect
    import click
    from pydantic import ValidationError
    from merit.config.models import MeritMainConfig
    from merit.metrics.base import BaseMetric, register_metric, get_metric # Updated import source
    # If CONFIG_VARIABLE_NAME is to be imported from cli.py to avoid defining it here:
    # from merit.cli import CONFIG_VARIABLE_NAME 

    config_path = Path(config_path_str).resolve()
    if not config_path.is_file():
        raise click.ClickException(f"Configuration file not found: {config_path}")

    module_name = config_path.stem
    spec = importlib.util.spec_from_file_location(module_name, config_path)
    if spec is None or spec.loader is None:
        raise click.ClickException(f"Could not load configuration file as a module: {config_path}")

    config_module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = config_module
    
    try:
        spec.loader.exec_module(config_module)
    except Exception as e:
        raise click.ClickException(f"Error executing configuration file {config_path}: {e}")

    custom_metrics_found: Dict[str, type] = {}
    for name, obj in inspect.getmembers(config_module):
        if inspect.isclass(obj) and issubclass(obj, BaseMetric) and obj is not BaseMetric:
            metric_name_attr = getattr(obj, 'name', None)
            if not metric_name_attr:
                click.secho(f"Warning: Custom metric class {obj.__name__} is missing a 'name' attribute. Skipping registration.", fg="yellow")
                continue
            try:
                get_metric(metric_name_attr)
            except ValueError:
                register_metric(obj)
                click.echo(f"Discovered and registered custom metric: {metric_name_attr} (class {obj.__name__})")
            custom_metrics_found[metric_name_attr] = obj

    if not hasattr(config_module, CONFIG_VARIABLE_NAME):
        raise click.ClickException(f"Configuration variable '{CONFIG_VARIABLE_NAME}' not found in {config_path}.")

    user_config_obj = getattr(config_module, CONFIG_VARIABLE_NAME)

    if isinstance(user_config_obj, MeritMainConfig):
        # Attach discovered custom metrics to the config object if it doesn't have them
        # This assumes MeritMainConfig has a _custom_metrics attribute or similar mechanism
        if not hasattr(user_config_obj, '_custom_metrics') or not user_config_obj._custom_metrics: # type: ignore
            user_config_obj._custom_metrics = custom_metrics_found # type: ignore
        return user_config_obj
    elif isinstance(user_config_obj, dict):
        try:
            parsed_config = MeritMainConfig(**user_config_obj)
            parsed_config._custom_metrics = custom_metrics_found # type: ignore
            return parsed_config
        except ValidationError as e:
            raise click.ClickException(
                f"Variable '{CONFIG_VARIABLE_NAME}' in {config_path} is a dict, but failed to parse as MeritMainConfig:\n{e}"
            )
        except Exception as e:
            raise click.ClickException(
                f"Error parsing dict config from '{CONFIG_VARIABLE_NAME}' in {config_path}: {e}"
            )
    else:
        raise click.ClickException(
            f"Variable '{CONFIG_VARIABLE_NAME}' in {config_path} is not MeritMainConfig or dict. Found: {type(user_config_obj).__name__}"
        )

# --- KB Utils --- 

class KBDataLoaderError(Exception):
    """Custom exception for knowledge base data loading errors."""
    pass

def load_knowledge_base_data(kb_config: KnowledgeBaseConfigPydantic) -> List[Dict[str, Any]]:
    """
    Loads data for the KnowledgeBase from the specified configuration.
    Returns a list of dictionaries.
    """
    if not kb_config.path:
        raise KBDataLoaderError(f"Path is not specified for knowledge base type '{kb_config.type}'.")

    file_path = Path(kb_config.path)
    if not file_path.is_file():
        raise KBDataLoaderError(f"Knowledge base file not found: {file_path}")

    if isinstance(kb_config, KnowledgeBaseCsvConfig):
        try:
            with open(file_path, mode='r', encoding=kb_config.encoding, newline='') as f:
                reader = csv.DictReader(f, delimiter=kb_config.delimiter)
                return [row for row in reader]
        except Exception as e:
            raise KBDataLoaderError(f"Error loading CSV file {file_path}: {e}")

    elif isinstance(kb_config, KnowledgeBaseJsonConfig):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                f.seek(0)
                data = []
                if kb_config.type == "jsonl" or (first_line.startswith('{') and first_line.endswith('}')):
                    for line in f:
                        if line.strip():
                            data.append(parse_json(line))
                elif first_line.startswith('['):
                    raw_data = json.load(f)
                    if isinstance(raw_data, list):
                        data = raw_data
                    else:
                        raise KBDataLoaderError(f"JSON file {file_path} was expected to contain a list/array at the root.")
                else:
                    raise KBDataLoaderError(f"Cannot determine format of JSON file: {file_path}. Not JSONL or root array.")
            if kb_config.json_path_to_documents:
                print(f"Warning: json_path_to_documents ('{kb_config.json_path_to_documents}') is noted but not fully implemented yet for complex paths.")
            return data
        except json.JSONDecodeError as e:
            raise KBDataLoaderError(f"Error decoding JSON file {file_path}: {e}")
        except Exception as e:
            raise KBDataLoaderError(f"Error loading JSON file {file_path}: {e}")
    else:
        raise NotImplementedError(f"Knowledge base type '{kb_config.type}' is not yet supported for data loading.")

