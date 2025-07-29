import click
from pathlib import Path
from typing import Tuple, Optional, List
from loguru import logger
from git import Repo, BadName
from .utils import (
    url_to_repo_name, install_lean, get_valid_versions, get_tag_sha,
    detect_lakefile, update_lakefile_toml, update_lakefile_lean,
    list_lookeng_cache, list_mathlib_cache, list_repo_cache, get_lookeng_versions, get_mathlib_versions
)
from .install import install_mathlib, install_repl, InstallationError
from lookeng.constants import DEFAULT_LEAN4_VERSION, MATHLIB_URL, REPL_URL, LOOKENG_CACHE_DIR
from lookeng.verifier import execute_lean_code
import subprocess


help_message = """
Lean Repo management CLI

A tool for managing Lean repositories.
"""

help_message = """
Lean REPL management CLI

A tool for managing Lean REPL installations and versions.
"""

@click.group(help=help_message)
@click.option("--verbose", "-v", count=True, help="Enable verbose output.")
def cli(verbose: int):
    """Lean4 management tool"""
    pass

@cli.command()
@click.option('-y', is_flag=True, help='Skip confirmation')
def clean(y):
    """Clean up olean cache"""
    cache_dir = Path(LOOKENG_CACHE_DIR / 'olean')
    all_dirs = list(cache_dir.iterdir())
    all_files = list(cache_dir.glob("**/*.olean"))
    if len(all_dirs) + len(all_files) == 0:
        click.echo("No cache found.")
        return
    if not y:
        click.echo(f"Detected {len(all_dirs)} directories and {len(all_files)} files.")
        # logger.debug(all_dirs[:10] + all_files[:10])
        click.confirm("Do you want to continue?", abort=True)
    for file in all_files:
        try:
            file.unlink()
        except Exception as e:
            logger.error(f"Failed to delete {file}: {e}")
    for dir in all_dirs:
        try:
            dir.rmdir()
        except Exception as e:
            logger.error(f"Failed to delete {dir}: {e}")
    click.echo("Cleaned up.")


@cli.command(name='list')
def versions():
    """List available lookeng cached repositories"""
    try:
        available_versions = get_lookeng_versions()
        cached_versions = list_lookeng_cache()
        click.echo("Available REPL versions:")
        click.echo()
        
        for version in available_versions:
            if version in cached_versions:
                click.echo(
                    f"{version} " + 
                    click.style("(installed)", fg="green")
                )
            else:
                click.echo(version)
        for version in cached_versions[::-1]:
            if version not in available_versions:
                click.echo(
                    f"{version} " +
                    click.style("(cached)", fg="yellow")
                )
    except Exception as e:
        click.echo(f"Failed to fetch versions: {e}", err=True)
        raise click.Abort()

@cli.command()
@click.argument('version', required=False)
@click.option('-f', '--force', is_flag=True, help='Force reinstall if already exists')
@click.option('-d', '--dest-dir', type=click.Path(), help='Destination directory for installation')
def install(version: Optional[str], force: bool, dest_dir: Optional[str]):
    """Install Lean REPL and mathlib"""
    try:
        # Validate version
        valid_versions = get_valid_versions(REPL_URL)
        if version is None:
            version = DEFAULT_LEAN4_VERSION
            logger.info(f"Using default version: {version}")
        if version not in valid_versions:
            raise click.BadParameter(f"Unknown version {version}")
        
        # Install REPL
        install_path = install_repl(version, force, dest_dir)
        
        click.echo(
            click.style(
                f"Successfully installed REPL {version or 'latest'} to {install_path}",
                fg="green"
            )
        )
    except subprocess.CalledProcessError as e:
        raise InstallationError(f"Command failed: {e.cmd}") from e
    except Exception as e:
        logger.error(f"Installation failed: {e}")
        raise click.Abort() from e

## mathlib
@cli.group()
def mathlib():
    """Manage Lean mathlib installations"""
    pass

@mathlib.command(name='install')
@click.argument('version', required=False)
@click.option('-f', '--force', is_flag=True, help='Force reinstall if already exists')
@click.option('-d', '--dest-dir', type=click.Path(), help='Destination directory for installation')
def install_matlhib_version(version: Optional[str], force: bool, dest_dir: Optional[str]):
    """Install a github repository"""
    try:
        # Validate version
        if version is None:
            version = DEFAULT_LEAN4_VERSION
            logger.info(f"Using default version: {version}")
        # Install repo
        install_path = install_mathlib(version, force, dest_dir)
        # Test installation
        logger.info('Testing command: import Mathlib\\n#eval s!"v{Lean.versionString}"')
        msg, err, code = execute_lean_code('import Mathlib\n#eval s!"v{Lean.versionString}"', working_dir=install_path)
        if code != 0:
            raise InstallationError(f"Installation failed: {err}")
        logger.info(f"Lean Version: {msg.strip()}")
        if err:
            logger.warning(f"Installation error: {err}")
        logger.info(f"Succesfully installed mathlib version {version}")
    except InstallationError as e:
        logger.error(f"Installation failed: {e}")
        raise click.Abort() from e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise click.Abort() from e

@mathlib.command(name='list')
@click.option('-m', '--max-num', type=int, default=10, help='Maximum number of versions to show')
def list_mathlib_versions(max_num:int=10):
    """List available mathlib versions and their installation status"""
    try:
        available_versions = get_valid_versions(MATHLIB_URL, exclude_nightly=True, update=False)
        if max_num > 0:
            available_versions = available_versions[:max_num]
        cached_versions = list_mathlib_cache()
        click.echo("Available versions(latest {}):".format(max_num))
        click.echo()
        for version in available_versions:
            if version in cached_versions:
                click.echo(
                    f"{version} " +
                    click.style("(installed)", fg="green")
                )
            else:
                click.echo(version)
        for version in cached_versions[::-1]:
            if version not in available_versions:
                click.echo(
                    f"{version} " +
                    click.style("(installed)", fg="green")
                )
    except Exception as e:
        click.echo(f"Failed to fetch versions: {e}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    cli()