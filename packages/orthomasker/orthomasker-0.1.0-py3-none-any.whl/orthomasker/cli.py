"""Command line interface for tif2geojson."""

import click
import sys
from pathlib import Path
from typing import Optional

from .converter import TifToGeoJsonConverter

@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option(
    "--sam-checkpoint", "-w",
    type=click.Path(exists=True, path_type=Path),
    default="sam_vit_h_4b8939.pth",
    help="Path to SAM model weights (.pth file).",
)
@click.option(
    "--model-type", "-m",
    type=click.Choice(["vit_h", "vit_l", "vit_b"], case_sensitive=False),
    default="vit_h",
    help="SAM model type (default: vit_h).",
)
@click.option(
    "--confidence-threshold", "-t",
    type=float,
    default=0.0,
    help="Minimum stability score (0-100) to keep a mask (default: 0.0, unfiltered).",
)
@click.option(
    "--tile-size", type=int, default=1024, help="Tile size for processing (default: 1024)."
)
@click.option(
    "--overlap", type=int, default=128, help="Tile overlap in pixels (default: 128)."
)
@click.option(
    "--class-name", type=str, default="sam_object", help="Class label for output features."
)
@click.option(
    "--fixed-bounds",
    nargs=4,
    type=float,
    default=None,
    help="Bounding box (minx miny maxx maxy) in image CRS.",
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Enable verbose output."
)
def main(
    input_file: Path,
    output_file: Path,
    sam_checkpoint: Path,
    model_type: str,
    confidence_threshold: float,
    tile_size: int,
    overlap: int,
    class_name: str,
    fixed_bounds: Optional[tuple],
    verbose: bool,
) -> None:
    """Convert TIF file to GeoJSON with SAM mask generation."""
    try:
        if verbose:
            click.echo(f"Processing {input_file}...")
            click.echo(f"SAM checkpoint: {sam_checkpoint}")
            click.echo(f"Model type: {model_type}")
            click.echo(f"Confidence threshold: {confidence_threshold}")
            click.echo(f"Tile size: {tile_size}, Overlap: {overlap}")
            if fixed_bounds:
                click.echo(f"Fixed bounds: {fixed_bounds}")

        converter = TifToGeoJsonConverter(
            sam_checkpoint=str(sam_checkpoint),
            model_type=model_type,
            confidence_threshold=confidence_threshold,
            tile_size=tile_size,
            overlap=overlap,
            class_name=class_name,
            verbose=verbose,
        )

        converter.convert(
            input_path=input_file,
            output_path=output_file,
            fixed_bounds=tuple(fixed_bounds) if fixed_bounds else None,
        )

        if verbose:
            click.echo(f"Successfully converted to {output_file}")
        else:
            click.echo("Conversion completed successfully!")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
