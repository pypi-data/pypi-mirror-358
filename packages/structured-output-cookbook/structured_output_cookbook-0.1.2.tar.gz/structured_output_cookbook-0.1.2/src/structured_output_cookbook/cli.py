"""Command line interface for structured output extraction."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import click

from .config import Config
from .extractor import StructuredExtractor
from .templates.email import EmailSchema
from .templates.event import EventSchema
from .templates.job_description import JobDescriptionSchema
from .templates.product_review import ProductReviewSchema
from .templates.recipe import RecipeSchema
from .utils import SchemaLoader, get_logger, setup_logger

# Available predefined templates
TEMPLATES = {
    "job": JobDescriptionSchema,
    "recipe": RecipeSchema,
    "product-review": ProductReviewSchema,
    "email": EmailSchema,
    "event": EventSchema,
}


def save_extraction_result(
    result_data: dict[str, Any],
    template_name: str,
    output_path: str | None = None,
    data_dir: str = "data",
) -> str:
    """Save extraction result to file and return the path."""
    if output_path:
        # Use specified path
        save_path = Path(output_path)
    else:
        # Generate automatic path in data directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{template_name}_extraction_{timestamp}.json"

        data_path = Path(data_dir)
        data_path.mkdir(exist_ok=True)
        save_path = data_path / filename

    # Ensure parent directory exists
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Save the file
    save_path.write_text(
        json.dumps(result_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return str(save_path)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def main(ctx: click.Context, debug: bool) -> None:
    """Structured Output Cookbook - Extract structured data from text using LLMs."""
    ctx.ensure_object(dict)

    config = Config.from_env()
    if debug:
        config.log_level = "DEBUG"

    setup_logger(config)
    ctx.obj["config"] = config
    ctx.obj["logger"] = get_logger(__name__)


@main.command()
def list_templates() -> None:
    """List available predefined templates."""
    click.echo("Available predefined templates:")
    for name, schema in TEMPLATES.items():
        click.echo(f"  {name}: {schema.get_schema_description()}")  # type: ignore[attr-defined]


@main.command()
@click.option(
    "--config-dir",
    default="config/schemas",
    help="Directory containing YAML schema files",
)
def list_schemas(config_dir: str) -> None:
    """List available custom YAML schemas."""
    loader = SchemaLoader(config_dir)
    schemas = loader.list_schemas_with_descriptions()

    if not schemas:
        click.echo(f"No custom schemas found in {config_dir}")
        click.echo("Create .yaml files in the config directory to add custom schemas.")
        return

    click.echo("Available custom schemas:")
    for name, description in schemas:
        click.echo(f"  {name}: {description}")


@main.command()
@click.argument("template", type=click.Choice(list(TEMPLATES.keys())))
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    help="Input text file",
)
@click.option("--text", "-t", help="Input text directly")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output JSON file (default: auto-generated in data/)",
)
@click.option("--data-dir", default="data", help="Directory for auto-generated outputs")
@click.option("--pretty", is_flag=True, help="Pretty print JSON output")
@click.option(
    "--no-save",
    is_flag=True,
    help="Don't save to file, only print to stdout",
)
@click.pass_context
def extract(
    ctx: click.Context,
    template: str,
    input_file: str | None,
    text: str | None,
    output: str | None,
    data_dir: str,
    pretty: bool,
    no_save: bool,
) -> None:
    """Extract data using a predefined template."""
    logger = ctx.obj["logger"]
    config = ctx.obj["config"]

    # Get input text
    if input_file:
        input_text = Path(input_file).read_text(encoding="utf-8")
    elif text:
        input_text = text
    else:
        click.echo("Error: Must provide either --input-file or --text", err=True)
        sys.exit(1)

    # Extract data
    extractor = StructuredExtractor(config)
    schema = TEMPLATES[template]

    logger.info(f"Extracting using template: {template}")
    result = extractor.extract(input_text, schema)  # type: ignore[arg-type]

    if not result.success:
        click.echo(f"Extraction failed: {result.error}", err=True)
        sys.exit(1)

    # Ensure we have data
    if result.data is None:
        click.echo("Error: Extraction succeeded but no data returned", err=True)
        sys.exit(1)

    # Format output
    indent = 2 if pretty else None
    output_json = json.dumps(result.data, indent=indent, ensure_ascii=False)

    # Save to file unless --no-save is specified
    if not no_save:
        save_path = save_extraction_result(result.data, template, output, data_dir)
        click.echo(f"✅ Results saved to {save_path}")

    # Always print to stdout if no output file specified or if pretty print requested
    if not output or pretty or no_save:
        click.echo("📄 Extraction Result:")
        click.echo(output_json)

    # Show stats
    if result.tokens_used:
        # Get accurate cost from extractor's cost tracker
        if hasattr(extractor, "cost_tracker") and extractor.cost_tracker.session_costs:
            last_request = extractor.cost_tracker.session_costs[-1]
            actual_cost = last_request["cost"]["total_cost"]
            click.echo(f"📊 Tokens used: {result.tokens_used}")
            click.echo(f"💰 Actual cost: ${actual_cost:.6f}")
        else:
            click.echo(f"📊 Tokens used: {result.tokens_used}")
            click.echo(
                f"💰 Estimated cost: ~${(result.tokens_used * 0.00001):.4f}",
            )  # Fallback


@main.command()
@click.argument("schema_name")
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    help="Input text file",
)
@click.option("--text", "-t", help="Input text directly")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output JSON file (default: auto-generated in data/)",
)
@click.option("--data-dir", default="data", help="Directory for auto-generated outputs")
@click.option(
    "--config-dir",
    default="config/schemas",
    help="Directory containing YAML schema files",
)
@click.option("--pretty", is_flag=True, help="Pretty print JSON output")
@click.option(
    "--no-save",
    is_flag=True,
    help="Don't save to file, only print to stdout",
)
@click.pass_context
def extract_custom(
    ctx: click.Context,
    schema_name: str,
    input_file: str | None,
    text: str | None,
    output: str | None,
    data_dir: str,
    config_dir: str,
    pretty: bool,
    no_save: bool,
) -> None:
    """Extract data using a custom YAML schema."""
    logger = ctx.obj["logger"]
    config = ctx.obj["config"]

    # Load YAML schema
    loader = SchemaLoader(config_dir)
    try:
        yaml_schema = loader.load_schema(schema_name)
    except FileNotFoundError:
        click.echo(f"Schema '{schema_name}' not found in {config_dir}", err=True)
        click.echo("Use 'list-schemas' command to see available schemas.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error loading schema '{schema_name}': {e}", err=True)
        sys.exit(1)

    # Get input text
    if input_file:
        input_text = Path(input_file).read_text(encoding="utf-8")
    elif text:
        input_text = text
    else:
        click.echo("Error: Must provide either --input-file or --text", err=True)
        sys.exit(1)

    # Extract data
    extractor = StructuredExtractor(config)

    logger.info(f"Extracting using custom schema: {schema_name}")
    result = extractor.extract_with_yaml_schema(input_text, yaml_schema)

    if not result.success:
        click.echo(f"Extraction failed: {result.error}", err=True)
        sys.exit(1)

    # Ensure we have data
    if result.data is None:
        click.echo("Error: Extraction succeeded but no data returned", err=True)
        sys.exit(1)

    # Format output
    indent = 2 if pretty else None
    output_json = json.dumps(result.data, indent=indent, ensure_ascii=False)

    # Save to file unless --no-save is specified
    if not no_save:
        save_path = save_extraction_result(result.data, schema_name, output, data_dir)
        click.echo(f"✅ Results saved to {save_path}")

    # Always print to stdout if no output file specified or if pretty print requested
    if not output or pretty or no_save:
        click.echo("📄 Extraction Result:")
        click.echo(output_json)

    # Show stats
    if result.tokens_used:
        # Get accurate cost from extractor's cost tracker
        if hasattr(extractor, "cost_tracker") and extractor.cost_tracker.session_costs:
            last_request = extractor.cost_tracker.session_costs[-1]
            actual_cost = last_request["cost"]["total_cost"]
            click.echo(f"📊 Tokens used: {result.tokens_used}")
            click.echo(f"💰 Actual cost: ${actual_cost:.6f}")
        else:
            click.echo(f"📊 Tokens used: {result.tokens_used}")
            click.echo(
                f"💰 Estimated cost: ~${(result.tokens_used * 0.00001):.4f}",
            )  # Fallback


@main.command()
@click.option(
    "--config-dir",
    default="config/schemas",
    help="Directory containing YAML schema files",
)
@click.pass_context
def validate_schemas(ctx: click.Context, config_dir: str) -> None:
    """Validate all custom YAML schemas."""
    logger = ctx.obj["logger"]
    loader = SchemaLoader(config_dir)
    schemas = loader.get_available_schemas()

    if not schemas:
        click.echo(f"No schemas found in {config_dir}")
        return

    click.echo(f"Validating {len(schemas)} schemas in {config_dir}...")

    valid_count = 0
    for schema_name in schemas:
        is_valid, error = loader.validate_schema_structure(schema_name)
        if is_valid:
            valid_count += 1
            click.echo(f"✅ {schema_name}: Valid")
        else:
            click.echo(f"❌ {schema_name}: {error}")

    click.echo(f"\n📊 Results: {valid_count}/{len(schemas)} schemas are valid")


@main.command()
@click.pass_context
def session_stats(ctx: click.Context) -> None:
    """Show session statistics for API usage."""
    config = ctx.obj["config"]

    # Create a temporary extractor to get session stats
    extractor = StructuredExtractor(config)
    stats = extractor.cost_tracker.get_session_stats()

    if stats["total_requests"] == 0:
        click.echo("No API requests made in this session.")
        return

    click.echo("�� Session Statistics")
    click.echo("=" * 30)
    click.echo(f"Total requests: {stats['total_requests']}")
    click.echo(f"Total tokens: {stats['total_tokens']:,}")
    click.echo(f"Total cost: ${stats['total_cost']:.6f}")
    click.echo(f"Average tokens per request: {stats['average_tokens_per_request']:.1f}")
    click.echo(f"Average cost per request: ${stats['average_cost_per_request']:.6f}")
    click.echo(f"Models used: {', '.join(stats['models_used'])}")
    click.echo(f"Extraction types: {', '.join(stats['extraction_types'])}")


@main.command()
@click.argument("input_files", nargs=-1, required=True, type=click.Path(exists=True))
@click.argument("template", type=click.Choice(list(TEMPLATES.keys())))
@click.option(
    "--output-dir",
    "-d",
    default="data/batch",
    help="Output directory for batch results",
)
@click.option(
    "--parallel",
    "-p",
    is_flag=True,
    help="Process files in parallel (experimental)",
)
@click.pass_context
def batch_extract(
    ctx: click.Context,
    input_files: tuple[str, ...],
    template: str,
    output_dir: str,
    parallel: bool,
) -> None:
    """Extract data from multiple files using a predefined template."""
    logger = ctx.obj["logger"]
    config = ctx.obj["config"]

    if parallel:
        click.echo("⚠️  Parallel processing is experimental and may hit rate limits")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    extractor = StructuredExtractor(config)
    schema = TEMPLATES[template]

    successful = 0
    failed = 0

    click.echo(f"🔄 Processing {len(input_files)} files with template: {template}")

    for i, input_file in enumerate(input_files, 1):
        click.echo(f"[{i}/{len(input_files)}] Processing {input_file}...")

        try:
            input_text = Path(input_file).read_text(encoding="utf-8")
            result = extractor.extract(input_text, schema)  # type: ignore[arg-type]

            if result.success and result.data:
                # Generate output filename
                input_name = Path(input_file).stem
                output_file = (
                    output_path
                    / f"{template}_{input_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )

                # Save result
                output_file.write_text(
                    json.dumps(result.data, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )

                click.echo(f"  ✅ Saved to {output_file}")
                successful += 1
            else:
                click.echo(f"  ❌ Failed: {result.error}")
                failed += 1

        except Exception as e:
            click.echo(f"  ❌ Error reading file: {e}")
            failed += 1

    click.echo(
        f"\n📊 Batch processing complete: {successful} successful, {failed} failed",
    )

    # Show session stats
    stats = extractor.cost_tracker.get_session_stats()
    if stats["total_requests"] > 0:
        click.echo(f"💰 Total cost: ${stats['total_cost']:.6f}")


@main.command()
@click.pass_context
def cost_analysis(ctx: click.Context) -> None:
    """Show cost analysis and model recommendations."""
    config = ctx.obj["config"]
    extractor = StructuredExtractor(config)

    # Get session stats
    stats = extractor.cost_tracker.get_session_stats()

    if stats["total_requests"] == 0:
        click.echo("No requests made. Run some extractions first to see cost analysis.")
        return

    click.echo("💰 Cost Analysis")
    click.echo("=" * 40)

    # Current session stats
    click.echo("Current session:")
    click.echo(f"  Requests: {stats['total_requests']}")
    click.echo(f"  Total cost: ${stats['total_cost']:.6f}")
    click.echo(f"  Avg cost/request: ${stats['average_cost_per_request']:.6f}")

    # Model recommendations based on usage
    usage_pattern = {
        "avg_total_tokens": stats.get("average_tokens_per_request", 1000),
        "avg_prompt_tokens": int(stats.get("average_tokens_per_request", 1000) * 0.8),
        "avg_completion_tokens": int(
            stats.get("average_tokens_per_request", 1000) * 0.2,
        ),
    }

    recommendations = extractor.cost_tracker.get_model_recommendations(usage_pattern)

    click.echo(
        f"\n🎯 Model Recommendations (based on {stats['average_tokens_per_request']:.0f} avg tokens):",
    )
    for model, info in recommendations.items():
        click.echo(f"  {model}:")
        click.echo(f"    Cost per request: ${info['cost_per_request']:.6f}")
        click.echo(f"    Cost per 1K requests: ${info['cost_per_1k_requests']:.2f}")
        click.echo(f"    Relative cost: {info['relative_cost']}")


if __name__ == "__main__":
    main()
