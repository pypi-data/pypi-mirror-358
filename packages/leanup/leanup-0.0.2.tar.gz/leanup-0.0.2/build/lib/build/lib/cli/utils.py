import shutil, re, os
from pathlib import Path
from typing import Tuple, Optional, List
from loguru import logger
from git import Repo, BadName
from lookeng import constants
from lookeng.utils import working_directory, execute_command
import toml


def url_to_repo_name(url:str) -> Tuple[str]:
    """Convert the url to the username and repo name."""
    try:
        url = url.split('.git')[0].rstrip('/')
        username, repo_name = url.split('/')[-2:]
        return username, repo_name
    except ValueError:
        raise ValueError(f"Invalid URL: {url}")

def url_to_prefix(url:str):
    """Convert the url to the prefix."""
    username, repo_name = url_to_repo_name(url)
    return f"{username}-{repo_name}"

def get_valid_versions(url:str, exclude_nightly:bool=False, update:bool=True) -> List[str]:
    """Get the valid tags of the repo."""
    prefix = url_to_prefix(url)
    repo_cache = constants.LOOKENG_CACHE_DIR / prefix
    if not repo_cache.exists():
        logger.info(f"No cache found, cloning repository to {repo_cache}")
        repo = Repo.clone_from(url, repo_cache)
    else:
        repo = Repo(repo_cache)
    if update:
        try:
            repo.remote().fetch(tags=True)
        except Exception as e:
            logger.warning(f"Failed to fetch tags: {e}")
            repo.git.gc()
            repo.git.remote('prune', 'origin')
            repo.remote().fetch(tags=True, force=True)
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime, reverse=True)
    versions = [tag.name for tag in tags]
    if exclude_nightly: # exclude nightly builds
        versions = [tag.name for tag in tags if 'nightly' not in tag.name]
    return versions
    
class InstallationError(Exception):
    pass

script = """
#!/bin/bash
set -e
curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | bash -s -- -y --default-toolchain none
source ~/.profile # source ~/.bashrc
"""

def install_lean():
    """Install Lean 4."""
    if shutil.which('elan') is not None:
        logger.info("Lean already installed")
        return True
    logger.info("Installing Lean...")
    with working_directory() as tmp_dir:
        temp_sh = Path(tmp_dir) / 'install_lean.sh'
        temp_sh.write_text(script)
        _, _, code = execute_command(['bash', 'install_lean.sh'], cwd=tmp_dir)
    if code == 0:
        logger.info("Lean installed successfully")
        return True
    return False

def list_repo_cache(prefix:str) -> List[str]:
    """
    Get the list of cached Lean versions.

    Returns:
        List[str]: The list of cached Lean versions.

    Example:
        >>> list_repo_cache()
        ['v4.7.0', 'v4.8.0', 'v4.10.0']
    """
    cache_dir = Path(constants.LOOKENG_CACHE_DIR)
    if not cache_dir.exists():
        return []
    
    # search for prefix-v* directories
    version_pattern = re.compile(f'{prefix}-(v.*)')
    versions = []
    for path in cache_dir.iterdir():
        if path.is_dir():
            match = version_pattern.match(path.name)
            if match:
                versions.append(match.group(1))
    return sorted(versions)

def read_repo_cache(prefix:str, version: str) -> Optional[Path]:
    """
    Read the repo cache for a given version.

    Args:
        prefix: The prefix of the repo to read
        version: The version of repo to read

    Returns:
        Path: The path to the repo cache directory. None if not found.
    """
    cache_dir = Path(constants.LOOKENG_CACHE_DIR)
    repo_dir = cache_dir / f"{prefix}-{version}"
    if repo_dir.exists():
        return repo_dir.resolve()
    return None

# set up for REPL
def list_lookeng_cache() -> List[str]:
    """
    获取已缓存的 REPL 版本列表
    
    Returns:
        List[str]: 已缓存的版本号列表，按版本号排序
    
    Example:
        >>> list_lookeng_cache()
        ['v4.7.0', 'v4.8.0', 'v4.10.0']
    """
    return list_repo_cache('repl')

def list_mathlib_cache() -> List[str]:
    """
    获取已缓存的 Mathlib 版本列表

    Returns:
        List[str]: 已缓存的版本号列表，按版本号排序

    Example:
        >>> list_mathlib_cache()
        ['v4.7.0', 'v4.8.0', 'v4.10.0']
    """
    return list_repo_cache('mathlib')

def read_lookeng_cache(version: str) -> Optional[Path]:
    return read_repo_cache('repl', version)

def read_mathlib_cache(version: str) -> Optional[Path]:
    """
    读取指定版本的 Mathlib 缓存

    Args:
        version: Mathlib 版本号

    Returns:
        Path: Mathlib 缓存目录路径，如果不存在则返回 None
    """
    return read_repo_cache('mathlib', version)

def get_lookeng_versions() -> List[str]:
    """
    获取 Lean 4 的有效版本列表

    Returns:
        List[str]: 有效版本列表
    """
    return get_valid_versions(constants.REPL_URL, update=False)

def get_mathlib_versions(exclude_nightly:bool=True) -> List[str]:
    """
    获取 Lean 4 的有效版本列表
    Args:
        exclude_nightly: 是否排除 nightly 版本，默认为 False
    Returns:
        List[str]: 有效版本列表
    """
    return get_valid_versions(constants.MATHLIB_URL, exclude_nightly=exclude_nightly, update=False)

def detect_lakefile(install_dir: Path) -> Tuple[Path, str]:
    """
    Detects the type of lakefile to use based on the presence of a lakefile.toml or lakefile.lean.
    """
    toml_file = install_dir / "lakefile.toml" 
    lean_file = install_dir / "lakefile.lean"
    
    if toml_file.exists():
        return toml_file, 'toml'
    elif lean_file.exists():
        return lean_file, 'lean'
    else:
        raise InstallationError("No lakefile found")

def update_lakefile_toml(file_path: Path, version: str):
    """update toml format lakefile"""
    try:
        if file_path.exists():
            config = toml.load(file_path)
        else:
            config = {}
        if 'require' not in config:
            config['require'] = []
        # add mathlib dependency
        mathlib_req = {
            'name': 'mathlib',
            'git': 'https://github.com/leanprover-community/mathlib4',
            'rev': version,
        }
        # remove existing mathlib requirement
        config['require'] = [r for r in config.get('require', []) 
                           if not (isinstance(r, dict) and r.get('name') == 'mathlib')]
        config['require'].append(mathlib_req)
        with open(file_path, 'w') as f:
            toml.dump(config, f)
    except Exception as e:
        raise InstallationError(f"Failed to update lakefile.toml: {e}")

def update_lakefile_lean(file_path: Path):
    """Update lean format lakefile"""
    try:
        # Read existing content
        content = file_path.read_text()
        
        # Add new mathlib require line
        mathlib_require = (
            f'\nrequire mathlib from git '
            '"https://github.com/leanprover-community/mathlib4.git" @ s!"v{Lean.versionString}"\n'
        )
        content += mathlib_require
        
        # Write back to file
        file_path.write_text(content)
    except Exception as e:
        raise InstallationError(f"Failed to update lakefile.lean: {e}")

def get_tag_sha(url: str, version: str) -> str:
    """Get commit SHA for specified tag"""
    if version not in get_valid_versions(url) and version not in get_valid_versions(url, update=True):
        raise InstallationError(f"Version {version} not found in {url}")
    prefix = url_to_prefix(url)
    repo_dir = Path(constants.LOOKENG_CACHE_DIR) / prefix
    repo = Repo(repo_dir)
    try:
        # 获取指定tag的引用
        tag_ref = repo.tags[version]
        # 获取commit SHA
        return tag_ref.commit.hexsha
    except (IndexError, KeyError) as e:
        raise InstallationError(f"Tag {version} not found: {e}")