import click
import importlib.util
import sys
import inspect
import json # Added for dumping evaluation results
from pathlib import Path
from merit.core.models import TestSet, Response # Added for TestSet.load() and system response object
from merit.api.client import AIAPIClientConfig # Added for system client init_args
from pydantic import ValidationError

from merit.config.models import MeritMainConfig
from merit.metrics.base import BaseMetric, register_metric, get_metric # Assuming global registry for now
from merit.metrics.base import get_metric
from merit.metrics.llm_measured import LLMMeasuredBaseMetric
from merit.core.models import Response # Ensure Response is imported
from merit.templates.templates import TemplateManager
from merit.utils import (
    load_config_from_file, # Restored import
    create_ai_client,
    load_knowledge_base_data,
    create_system_client,
) # Imports from merit.utils
from merit.knowledge.knowledgebase import KnowledgeBase # Adjusted import
from merit.testset_generation.generator import TestSetGenerator # Adjusted import
from merit.evaluation.evaluators.rag import RAGEvaluator as Evaluator # Use RAGEvaluator

@click.group()
def merit_cli():
    """Monitoring, Evaluation, Reporting, Inspection, Testing framework for AI systems."""
    pass

@merit_cli.command()
@click.option('--config', 
              type=click.Path(exists=True, dir_okay=False, readable=True),
              required=True, 
              help='Path to the MERIT configuration file (e.g., merit.config.py).')
def start(config: str):
    """Starts a MERIT evaluation run using the provided configuration file."""
    click.echo(f"MERIT starting with config file: {config}")
    
    try:
        merit_config = load_config_from_file(config)
        click.echo(f"Successfully loaded configuration from '{config}'.")
        # click.echo(f"Loaded config object: {merit_config.model_dump_json(indent=2)}")

        generated_test_set_result = None
        
    except Exception as e:
        click.secho(f"Error loading or processing configuration: {e}", fg="red", err=True)
        raise click.exceptions.Exit(1)

        # For debugging, you might want to print the full traceback
        # import traceback
        # traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    merit_cli()

