import json
import traceback
from pathlib import Path
from typing import Any

import typer

from .exporters.base_exporter import BaseExporter
from .exporters.utils.constants import DEFAULT_SCHEMA, EXPORT_FORMATS
from .exporters.utils.exporter_config import EXPORTER_CLASSES
from .generator import DataGenerator
from .providers import FakerProvider, MimesisProvider
from .schemas import DataType, FieldSchema, GeneratorConfig


def load_schema(schema_path: Path) -> dict[str, Any]:
    """Load schema from a JSON file.

    Args:
        schema_path: Path to the JSON schema file

    Returns:
        dict[str, Any]: Loaded schema as a dictionary

    Raises:
        FileNotFoundError: If schema file doesn't exist
        json.JSONDecodeError: If schema file contains invalid JSON

    """
    with open(schema_path, encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Schema file does not contain a JSON object.")
        return data


app = typer.Typer()

OUTPUT_PATH_OPTION = typer.Option(..., "--output", "-o", help="Output file path")
FORMAT_OPTION = typer.Option(
    "csv", "--format", "-f", help=f"Output format ({EXPORT_FORMATS})"
)
ROWS_OPTION = typer.Option(10, "--rows", "-r", help="Number of rows to generate")
SCHEMA_PATH_OPTION = typer.Option(None, "--schema", "-s", help="Path to schema file")
DEBUG_OPTION = typer.Option(False, "--debug", "-d", help="Enable debug output")
PROVIDER_OPTION = typer.Option(
    "mimesis", "--provider", "-p", help="Data provider (faker or mimesis)"
)


@app.command()
def generate(
    output: Path = OUTPUT_PATH_OPTION,
    format: str = FORMAT_OPTION,
    rows: int = ROWS_OPTION,
    schema_path: Path | None = SCHEMA_PATH_OPTION,
    debug: bool = DEBUG_OPTION,
    provider: str = PROVIDER_OPTION,
) -> None:
    """Generate synthetic data based on the provided schema."""
    try:
        if debug:
            typer.echo(
                f"Starting data generation with schema: {schema_path}", err=False
            )
        if schema_path:
            schema = load_schema(schema_path)
        else:
            schema = DEFAULT_SCHEMA

        # Check if the number of rows is zero or negative
        if rows <= 0:
            raise ValueError("Number of rows must be greater than zero")

        # Convert schema to field schemas
        if debug:
            typer.echo(f"Loaded schema: {schema}", err=False)
        fields = []
        for name, field_def in schema.items():
            if isinstance(field_def, dict):
                if "type" not in field_def:
                    raise ValueError(f"Field '{name}' missing required 'type' key")

                # Validate min and max values based on type
                min_value = field_def.get("min")
                max_value = field_def.get("max")
                field_type = DataType(field_def["type"])

                if field_type in {DataType.INTEGER, DataType.BIGINT}:
                    if min_value is not None and not isinstance(min_value, int):
                        raise ValueError(
                            f"Invalid min value for field '{name}': {min_value}"
                        )
                    if max_value is not None and not isinstance(max_value, int):
                        raise ValueError(
                            f"Invalid max value for field '{name}': {max_value}"
                        )
                elif field_type == DataType.STRING:
                    if min_value is not None or max_value is not None:
                        raise ValueError(
                            f"Invalid min or max value for field '{name}': "
                            f"{min_value}, {max_value}"
                        )

                field_schema = FieldSchema(
                    name=name,
                    type=field_type,
                    enum_values=field_def.get("values"),
                    min_value=min_value,
                    max_value=max_value,
                    right_digits=field_def.get("right_digits"),
                    value_provider=field_def.get("provider_field")
                    or field_def.get("faker"),
                    pattern=field_def.get("pattern"),
                )
                fields.append(field_schema.model_dump())
            else:
                fields.append(
                    FieldSchema(name=name, type=DataType(field_def)).model_dump()
                )

        # Validate export format
        if format not in EXPORT_FORMATS:
            raise ValueError(f"Unsupported format: {format}")

        # Validate provider
        if provider.lower() not in ["faker", "mimesis"]:
            raise ValueError(f"Unsupported provider: {provider}")

        # Create generator config
        if debug:
            typer.echo(f"Converted fields: {fields}", err=False)
        config = GeneratorConfig(
            fields=fields, row_count=rows, export_format=format, output_path=str(output)
        )

        # Generate data
        if debug:
            typer.echo(f"Generator config: {config}", err=False)

        # Select provider
        data_provider = (
            MimesisProvider() if provider.lower() == "mimesis" else FakerProvider()
        )
        generator = DataGenerator(provider=data_provider)
        data = generator.generate_data(config.fields, config.row_count)

        # Export data
        exporter = get_exporter(config.export_format)
        if debug:
            typer.echo(f"Generated data: {data}", err=False)

        exporter.export(data, config.output_path, schema=schema)

        typer.echo(f"Successfully generated {rows} rows of data to {output}")
        return

    except FileNotFoundError as e:
        typer.echo(f"Schema file not found: {e}", err=True)
        raise typer.Exit(code=1) from e
    except ValueError as e:
        typer.echo(f"Value Error: {e}", err=True)
        raise typer.Exit(code=1) from e
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        typer.echo(f"Exception type: {type(e).__name__}", err=True)
        typer.echo(f"Exception args: {e.args}", err=True)
        typer.echo(f"Traceback: {traceback.format_exc()}", err=True)
        raise typer.Exit(code=1) from e


def get_exporter(format: str) -> BaseExporter:
    """Return the appropriate exporter based on the format."""
    exporters = EXPORTER_CLASSES
    if format not in exporters:
        raise ValueError(f"Unsupported format: {format}")
    return exporters[format]


if __name__ == "__main__":
    app()
