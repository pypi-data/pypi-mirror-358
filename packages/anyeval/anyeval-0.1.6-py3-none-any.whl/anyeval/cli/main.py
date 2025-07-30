import os
import sys
import threading
import time
import webbrowser
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import typer
import uvicorn

from anyeval.packer import pack_evaluation, merge_evaluations

# Change from default command to explicit subcommands
app = typer.Typer(add_completion=False)


def start_backend(files_info, host="127.0.0.1", port=8000, data_directory=None) -> None:
    """Start the backend server."""
    from anyeval.backend.app import create_app

    if isinstance(files_info, str):
        # Single file case
        df = pd.read_parquet(files_info)
        file_name = os.path.basename(files_info)
        files_list = [{"name": file_name, "path": files_info}]
        # Determine data directory from file path if not provided
        if data_directory is None:
            data_directory = Path(files_info).parent
    else:
        # Multiple files case
        df = pd.concat(
            [pd.read_parquet(file_info["path"]) for file_info in files_info],
            ignore_index=True,
        )
        files_list = files_info
        # Determine data directory from first file path if not provided
        if data_directory is None and files_info:
            data_directory = Path(files_info[0]["path"]).parent

    # Create and run the app with the loaded data and files info
    api_app = create_app(df, files_list, data_directory)
    uvicorn.run(api_app, host=host, port=port)


@app.command()
def run(
    parquet_path: Path = typer.Argument(
        ..., help="Parquet file, directory containing parquet files, or zip file", exists=True,
    ),
    listen: str = typer.Option(
        "127.0.0.1", help="IP address to listen on (default: 127.0.0.1)",
    ),
    port: int = typer.Option(8000, help="Port to listen on (default: 8000)"),
    open_browser: bool = typer.Option(True, help="Automatically open browser (default: True)"),
    zip: bool = typer.Option(False, "--zip", help="Run directly from a zip file"),
) -> None:
    """Run evaluation for a parquet file, directory, or zip file."""
    # Handle zip file input
    temp_dir = None
    actual_parquet_path = parquet_path
    
    if zip or str(parquet_path).endswith('.zip'):
        if not str(parquet_path).endswith('.zip'):
            typer.echo(f"Error: --zip flag used but '{parquet_path}' is not a zip file.")
            sys.exit(1)
        
        typer.echo(f"Extracting zip file: {parquet_path}")
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            with zipfile.ZipFile(parquet_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Look for data directory in extracted content
            data_dir = temp_dir / "data"
            if data_dir.exists():
                actual_parquet_path = data_dir
            else:
                # If no data directory, use temp_dir directly
                actual_parquet_path = temp_dir
                
            typer.echo(f"Extracted to: {actual_parquet_path}")
            
        except zipfile.BadZipFile:
            typer.echo(f"Error: '{parquet_path}' is not a valid zip file.")
            sys.exit(1)
        except Exception as e:
            typer.echo(f"Error extracting zip file: {e}")
            sys.exit(1)
    
    # Process the input path
    files_info = []

    if actual_parquet_path.is_dir():
        # If it's a directory, get all parquet files
        for file_path in actual_parquet_path.glob("*.parquet"):
            file_name = file_path.name
            typer.echo(f"Found parquet file: {file_name}")
            files_info.append({"name": file_name, "path": str(file_path)})

        if not files_info:
            typer.echo(f"Error: No parquet files found in directory '{actual_parquet_path}'.")
            if temp_dir:
                import shutil
                shutil.rmtree(temp_dir)
            sys.exit(1)

    elif actual_parquet_path.is_file() and str(actual_parquet_path).endswith(".parquet"):
        # Single file case
        typer.echo(f"Processing single parquet file: {actual_parquet_path}")
        files_info = str(actual_parquet_path)

    else:
        typer.echo(f"Error: '{actual_parquet_path}' is not a valid parquet file or directory.")
        if temp_dir:
            import shutil
            shutil.rmtree(temp_dir)
        sys.exit(1)

    # Start the backend in a separate thread
    backend_thread = threading.Thread(
        target=start_backend, args=(files_info, listen, port, actual_parquet_path), daemon=True,
    )
    backend_thread.start()

    # Give the server a moment to start
    time.sleep(1)

    # Open the browser if open_browser is True
    typer.echo(f"Server running at http://{listen}:{port}")
    if open_browser:
        typer.echo("Opening browser")
        webbrowser.open(f"http://{listen}:{port}")

    typer.echo("Press Ctrl+C to stop the server")

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        typer.echo("Shutting down services...")
    finally:
        # Clean up temporary directory if it was created
        if temp_dir:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            typer.echo("Cleaned up temporary files")

    sys.exit(0)


@app.command()
def pack(
    source: Path = typer.Argument(
        ..., help="Parquet file or directory containing parquet files to pack", exists=True,
    ),
    output: Path = typer.Argument(
        ..., help="Output directory or zip file for the packed evaluation",
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", "-f", help="Overwrite output directory if it exists"
    ),
    zip: bool = typer.Option(False, "--zip", help="Create a zip file instead of a directory"),
) -> None:
    """Pack evaluation data and resources into a portable folder structure or zip file."""
    try:
        if zip and not str(output).endswith('.zip'):
            # If --zip flag is used, ensure output has .zip extension
            output = output.with_suffix('.zip')
        
        if zip:
            # Create zip file
            typer.echo(f"Packing evaluation from '{source}' to zip file '{output}'...")
            
            # Check if zip file already exists
            if output.exists() and not overwrite:
                typer.echo(f"❌ Error: Zip file already exists: {output}")
                typer.echo("   Use --overwrite to replace the existing file.")
                sys.exit(1)
            
            # Create temporary directory for packing
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir) / "packed_eval"
                
                # Pack to temporary directory first
                metadata = pack_evaluation(source, temp_path, overwrite=True)
                
                # Create zip file from temporary directory
                typer.echo("Creating zip file...")
                with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in temp_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(temp_path)
                            zipf.write(file_path, arcname)
                
                typer.echo(f"✅ Successfully packed evaluation to zip!")
                typer.echo(f"   Pack ID: {metadata['pack_id']}")
                typer.echo(f"   Parquet files: {len(metadata['parquet_files'])}")
                typer.echo(f"   Resources packed: {metadata['packed_resources']}")
                typer.echo(f"   Output: {output}")
                typer.echo("")
                typer.echo("🚀 To use the packed evaluation:")
                typer.echo(f"   anyeval run --zip {output}")
        else:
            # Create directory
            typer.echo(f"Packing evaluation from '{source}' to '{output}'...")
            
            # Pack the evaluation
            metadata = pack_evaluation(source, output, overwrite=overwrite)
            
            typer.echo(f"✅ Successfully packed evaluation!")
            typer.echo(f"   Pack ID: {metadata['pack_id']}")
            typer.echo(f"   Parquet files: {len(metadata['parquet_files'])}")
            typer.echo(f"   Resources packed: {metadata['packed_resources']}")
            typer.echo(f"   Output: {output}")
            typer.echo("")
            typer.echo("🚀 To use the packed evaluation:")
            typer.echo(f"   anyeval run {output / 'data'}")
        
    except FileExistsError as e:
        typer.echo(f"❌ Error: {e}")
        typer.echo("   Use --overwrite to replace the existing directory.")
        sys.exit(1)
    except Exception as e:
        typer.echo(f"❌ Error packing evaluation: {e}")
        sys.exit(1)


@app.command()
def merge(
    source1: Path = typer.Argument(
        ..., help="First packed evaluation folder to merge", exists=True,
    ),
    source2: Path = typer.Argument(
        ..., help="Second packed evaluation folder to merge", exists=True,
    ),
    output: Path = typer.Argument(
        ..., help="Output directory for the merged evaluation",
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", "-f", help="Overwrite output directory if it exists"
    ),
) -> None:
    """Merge two packed evaluation folders into a single evaluation."""
    try:
        typer.echo(f"Merging evaluations from '{source1}' and '{source2}' to '{output}'...")
        
        # Merge the evaluations
        metadata = merge_evaluations(source1, source2, output, overwrite=overwrite)
        
        typer.echo(f"✅ Successfully merged evaluations!")
        typer.echo(f"   Merge ID: {metadata['pack_id']}")
        typer.echo(f"   Parquet files: {len(metadata['parquet_files'])}")
        typer.echo(f"   Resources: {metadata['resource_count']}")
        
        # Show file conflicts if any
        if metadata.get('merge_info', {}).get('file_conflicts'):
            typer.echo("   File conflicts resolved:")
            for category, conflicts in metadata['merge_info']['file_conflicts'].items():
                typer.echo(f"     {category}:")
                for conflict in conflicts:
                    typer.echo(f"       {conflict}")
        
        typer.echo(f"   Output: {output}")
        typer.echo("")
        typer.echo("🚀 To use the merged evaluation:")
        typer.echo(f"   anyeval run {output / 'data'}")
        
    except FileExistsError as e:
        typer.echo(f"❌ Error: {e}")
        typer.echo("   Use --overwrite to replace the existing directory.")
        sys.exit(1)
    except Exception as e:
        typer.echo(f"❌ Error merging evaluations: {e}")
        sys.exit(1)


# Add this function to serve as a default command
@app.callback()
def callback() -> None:
    """AnyEval - Universal Evaluation for Gen AI."""


if __name__ == "__main__":
    app()
