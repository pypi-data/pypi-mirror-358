#!/usr/bin/env python3
"""
Script to run damply project audit on all directories in a given path
and combine the results into a single JSON file
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import click


def check_requirements():
    """Check if required tools are available."""
    # Check for damply
    try:
        result = subprocess.run(
            ["damply", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        click.echo(f"{result.stdout.strip()} is available.")
    except (subprocess.SubprocessError, FileNotFoundError):
        click.echo("damply is not available or --help failed.")
        click.echo("please install with `uv tool install damply@latest --compile-bytecode` (on the login node)")
        sys.exit(1)

    # Check for jq
    try:
        result = subprocess.run(
            ["jq", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        click.echo(f"jq {result.stdout.strip()} is available.")
    except (subprocess.SubprocessError, FileNotFoundError):
        click.echo("Error: jq is required for JSON processing but not found.")
        click.echo("Please install jq using your system package manager (i.e `pixi global install jq` or `apt-get install jq`)")
        sys.exit(1)


def get_project_group(source_dir):
    """Extract the project group from the source directory path."""
    parts = Path(source_dir).parts
    
    if len(parts) < 4 or parts[1] != "cluster" or parts[2] != "projects":
        click.echo("Error: Input directory must start with /cluster/projects/bhklab or /cluster/projects/radiomics.")
        sys.exit(1)
        
    project_group = parts[3]
    if project_group not in ["bhklab", "radiomics"]:
        click.echo(f"Error: Invalid project group '{project_group}'.")
        click.echo("Input directory must start with /cluster/projects/bhklab or /cluster/projects/radiomics.")
        sys.exit(1)
        
    click.echo(f"INFO: Project group is '{project_group}'")
    return project_group


def get_parents_path(project_group, source_dir):
    """Get the relative path from the project root."""
    base_path = Path(f"/cluster/projects/{project_group}")
    source_path = Path(source_dir)
    
    try:
        parents_path = source_path.relative_to(base_path)
        click.echo(f"INFO: Parents path is '{parents_path}'")
        return str(parents_path)
    except ValueError:
        click.echo("Error: Source directory is not within the project path.")
        sys.exit(1)


def run_damply_audit(directory, output_file, error_file):
    """Run damply project audit on a directory."""
    try:
        result = subprocess.run(
            ["damply", "project", "--force-compute-details", "--json", directory],
            capture_output=True,
            text=True,
            check=True
        )
        with open(output_file, 'w') as f:
            f.write(result.stdout)
        return True
    except subprocess.SubprocessError as e:
        with open(error_file, 'w') as f:
            f.write(str(e))
            if e.stderr:
                f.write("\n" + e.stderr)
        return False


def combine_json_files(output_file, source_file, json_files, audit_date):
    """Combine all JSON files into a single output file."""
    # Read source directory data
    with open(source_file, 'r') as f:
        source_data = json.load(f)
    
    # Create initial combined data
    combined_data = {
        "audit_date": audit_date,
        "source_directory": source_data,
        "directories": {}
    }
    
    # Add data from each directory
    for json_file in json_files:
        if not os.path.exists(json_file) or os.path.getsize(json_file) == 0:
            continue
            
        try:
            with open(json_file, 'r') as f:
                dir_data = json.load(f)
            
            dir_name = os.path.basename(json_file).replace('.json', '')
            combined_data["directories"][dir_name] = dir_data
        except json.JSONDecodeError:
            click.echo(f"Warning: Invalid JSON in {json_file}, skipping")
    
    # Write combined data to output file
    with open(output_file, 'w') as f:
        json.dump(combined_data, f, indent=2)


@click.command()
@click.argument('directory_to_scan', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def audit_directory(directory_to_scan):
    """Run damply project audit on all directories in a given path and combine the results."""
    source_dir = os.path.realpath(directory_to_scan)
    
    # Check requirements
    check_requirements()
    
    # Get timestamps
    now = datetime.now()
    today = now.strftime("%Y-%m-%dT%H-%M-%S")
    today_date = now.strftime("%Y-%m-%d")
    
    # Get project info
    project_group = get_project_group(source_dir)
    parents_path = get_parents_path(project_group, source_dir)
    
    # Setup directories
    results_dir = Path(f"/cluster/projects/{project_group}/admin/audit/results/{today_date}/{parents_path}")
    temp_dir = results_dir / ".tmp" / f"damply_audit_{os.path.basename(source_dir)}"
    output_file = results_dir / "audit.json"
    
    click.echo(f"INFO: Results directory is '{results_dir}'")
    click.echo(f"INFO: Temporary directory is '{temp_dir}'")
    click.echo(f"INFO: Output file is '{output_file}'")
    
    # Create directories
    results_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Process source directory
    click.echo("Processing source directory itself...")
    source_output = temp_dir / "source_directory.json"
    source_error = temp_dir / "source_directory.error"
    success = run_damply_audit(source_dir, source_output, source_error)
    
    if not success:
        click.echo("Error processing source directory")
        with open(source_error, 'r') as f:
            click.echo(f.read())
    else:
        if os.path.exists(source_error):
            os.unlink(source_error)
    
    # Process each subdirectory
    for item in os.listdir(source_dir):
        dir_path = os.path.join(source_dir, item)
        if os.path.isdir(dir_path):
            click.echo(f"Processing {item}...")
            dir_output = temp_dir / f"{item}.json"
            dir_error = temp_dir / f"{item}.error"
            success = run_damply_audit(dir_path, dir_output, dir_error)
            
            if not success:
                click.echo(f"Error processing {item}")
                with open(dir_error, 'r') as f:
                    click.echo(f.read())
            else:
                if os.path.exists(dir_error):
                    os.unlink(dir_error)
    
    # Find all JSON files (excluding source directory)
    json_files = [
        str(f) for f in temp_dir.glob("*.json") 
        if f.name != "source_directory.json"
    ]
    
    click.echo(f"Combining {len(json_files)} JSON files into a single object...")
    
    # Combine JSON files
    combine_json_files(
        str(output_file), 
        str(source_output), 
        json_files, 
        today
    )
    
    # Clean up temporary files
    if output_file.exists():
        click.echo("Cleaning up temporary files...")
        shutil.rmtree(temp_dir)
        
        # Remove empty directories
        for dirpath, dirnames, filenames in os.walk(results_dir, topdown=False):
            if not dirnames and not filenames and dirpath != str(results_dir):
                os.rmdir(dirpath)
    
    click.echo(f"Audit complete. Results stored in {output_file}")


if __name__ == "__main__":
    audit_directory()
