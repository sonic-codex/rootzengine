import logging
from pathlib import Path

import typer

from rootzengine.core.config import AzureConfig, load_config
from rootzengine.storage.azure import AzureStorageManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = typer.Typer()


@app.command()
def download(
    output_dir: Path = typer.Option(
        "data",
        "--output-dir",
        "-o",
        help="The local base directory to download files into.",
    ),
    prefix: str = typer.Option(
        "processed/",
        "--prefix",
        "-p",
        help="The cloud folder to download from (e.g., 'processed/', 'midi/').",
    ),
    config_path: Path = typer.Option(
        "configs/azure.yaml", "--config", "-c", help="Path to the Azure config file."
    ),
):
    """
    Download data from Azure Blob Storage.
    """
    typer.echo(f"Starting download from prefix '{prefix}' in Azure...")

    try:
        azure_config = load_config(AzureConfig, config_path)
        storage_manager = AzureStorageManager(azure_config)

        destination = output_dir
        destination.mkdir(parents=True, exist_ok=True)

        storage_manager.download_blobs(destination_dir=destination, prefix=prefix)

        typer.secho(
            f"✅ Download complete. Data saved in {destination.resolve()}", fg=typer.colors.GREEN
        )
    except (FileNotFoundError, ValueError) as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()