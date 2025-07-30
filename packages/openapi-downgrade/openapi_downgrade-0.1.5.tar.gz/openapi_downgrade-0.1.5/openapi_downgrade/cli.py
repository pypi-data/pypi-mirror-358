import typer
from openapi_downgrade.converter.loader import load_spec
from openapi_downgrade.converter.transformer import convert_spec
import json

app = typer.Typer()

@app.command()
def convert(input: str, output: str):
    """
    Convert an OpenAPI 3.1.x spec to 3.0.x.
    Supports file paths or URLs.
    """
    try:
        spec = load_spec(input)
        converted = convert_spec(spec)

        with open(output, "w") as f:
            json.dump(converted, f, indent=2)

        typer.echo(f"\U00002705 Converted and saved to: {output}")
    except Exception as e:
        typer.echo(f"\u274C Error: {e}")

if __name__ == "__main__":
    app()
