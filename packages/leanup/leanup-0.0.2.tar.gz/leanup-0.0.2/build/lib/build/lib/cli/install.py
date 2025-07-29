from lookeng.utils import working_directory, execute_command, execute_popen_command
from lookeng.constants import MATHLIB_URL
from lookeng import constants
import os
import toml, subprocess, shutil, re
from pathlib import Path
from typing import Tuple, Optional, List
from loguru import logger
from git import Repo, BadName
from .utils import (
    url_to_repo_name, install_lean, get_valid_versions, get_tag_sha,
    detect_lakefile, update_lakefile_toml, update_lakefile_lean, url_to_prefix
)

class InstallationError(Exception):
    pass

def install_lean_repo(url:str, version: str,
                      prefix:Optional[str]=None,
                      force: bool = False, 
                      dest_dir: Optional[str] = None,
                      with_mathlib:bool=False,
                      build_cmds:Optional[list[str]]=None) -> Path:
    """
    Download and build Lean 4 Repo.
    
    Args:
        url: Lean repository URL
        version: Lean tag (e.g. 'v4.10.0')
        prefix: Prefix for the installation directory, extract from url by default
        force: If True, overwrite existing installation
        dest_dir: Custom installation directory
        build_cmds: List of build commands to run
        
    Returns:
        Path: Installation directory path
        
    Raises:
        InstallationError: If installation fails
    """
    # make sure `elan`` is installed
    if shutil.which('lake') is None:
        install_lean()
        os.environ['PATH'] += os.pathsep + os.path.expanduser('~/.elan/bin')
    # default build commands
    if build_cmds is None:
        build_cmds = ['lake update -R', 'lake build']
    # Setup paths
    dest_dir = dest_dir and Path(dest_dir).resolve()
    if dest_dir is not None and not force and dest_dir.exists():
        logger.info(f"Destination directory {dest_dir} already exists")
        return dest_dir

    # Check existing cache
    username, repo_name = url_to_repo_name(url)
    prefix = prefix or url_to_prefix(url)
    cache_dir = Path(constants.LOOKENG_CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{prefix}-{version}"
    
    if cache_path.exists() and not force:
        logger.info(f"Version {version} already installed at {cache_path}")
        if dest_dir is not None:
            _, err, code = execute_command(["cp", "-r", cache_path, dest_dir])
            if code != 0:
                raise InstallationError(f"Failed to copy cache to destination directory: {err}")
            return dest_dir
        return cache_path
    
    work_dir = dest_dir and dest_dir.parent # set None if not specified
    with working_directory(work_dir, chdir=True) as work_dir:
        if dest_dir is None: # use temp dir
            repo_path = Path(work_dir) / f"{prefix}-{version}"
            logger.debug(f"Working in temporary directory: {work_dir}")
        else:
            repo_path = dest_dir
            logger.debug(f"Working in directory: {work_dir}")
            if repo_path.exists(): # remove existing directory
                shutil.rmtree(repo_path)
        cache_repo_base = cache_dir / url_to_prefix(url) # track the latest repo
        # Create new repo
        try:
            if not (version in get_valid_versions(url, update=False) or version in get_valid_versions(url, update=False)):
                raise InstallationError(f"Unknown version: {version}")
            Repo.clone_from(str(cache_repo_base), repo_path, branch=version)
        except BadName:
            raise InstallationError(f"Version {version} not found in repository")
        if with_mathlib and repo_name not in ['mathlib', 'mathlib4']:
            # update lakefile
            lakefile, file_type = detect_lakefile(repo_path)
            mathlib_rev = get_tag_sha(MATHLIB_URL, version)
            logger.debug(f"Detected {file_type} lakefile at {lakefile}")
            if file_type == 'toml':
                update_lakefile_toml(lakefile, mathlib_rev)
            else:
                update_lakefile_lean(lakefile, version)
        for cmd in build_cmds:
            logger.info(f"Running command: {cmd}")
            _, err, code = execute_command(cmd.split(), cwd=repo_path, capture_output=False)
            if code != 0:
                raise InstallationError(f"Failed to run {cmd}: {err}")

        # Save to cache
        if cache_path.exists():
            shutil.rmtree(cache_path)
        logger.debug(f"Saving installation to cache: {cache_path}")
        _, err, code = execute_command(["mv", repo_path, cache_path])
        if code != 0:
            raise InstallationError(f"Failed to save installation to cache: {err}")
    if dest_dir is None:
        repo_path = cache_path # return the cache path
    logger.info(f"Setup completed successfully in {repo_path}")
    return repo_path

def install_mathlib(version: str,
                    force: bool = False,
                    dest_dir: Optional[str] = None):
    """Install mathlib4."""
    build_cmds = ['lake exe cache get', 'lake build']
    return install_lean_repo(MATHLIB_URL, version, prefix='mathlib', force=force, dest_dir=dest_dir, build_cmds=build_cmds)

# set up REPL
def install_repl( version: str
                , force: bool = False
                , dest_dir:Optional[Path] = None
                , url:Optional[str]=None) -> Path:
    """
    Install specified version of Lean REPL
    
    Args:
        version: REPL version to install, None for latest
        force: Force reinstall if already exists
        dest_dir: Destination directory for installation
    
    Returns:
        Path to installed REPL
    
    Raises:
        InstallationError: If installation fails
    """
    if url is None:
        url = 'https://github.com/leanprover-community/repl'
    return install_lean_repo(url, version, prefix='repl', force=force, dest_dir=dest_dir, with_mathlib=True)
