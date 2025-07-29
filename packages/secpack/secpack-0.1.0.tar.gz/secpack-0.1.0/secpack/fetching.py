import re
import os
import requests
import subprocess

from urllib.parse import urlparse
from pathlib import Path, PurePosixPath

from secpack.security import SecureTemporaryDirectory
from secpack.logger import logger, log_error
from secpack.archiving import (
    archive_folder,
    archive_file,
    archive_file_from_path,
    archive_multiple_files,
)

from secpack.git_url import parse_git_url

# --- Check if the target path is safely within the base path ---
def is_safe_path(base_path: str, target_path: str) -> bool:
    # Resolve absolute paths to avoid path traversal attacks
    base = Path(base_path).resolve()
    target = Path(target_path).resolve()

    try:
        # Check if target is a subpath of base
        target.relative_to(base)
        return True
    except ValueError:
        # target is outside base path
        return False

# --- Source type checks ---

def is_local_file(path: str) -> bool:
    # Check if path is an existing file on the local filesystem
    return os.path.isfile(path)

def is_local_folder(path: str) -> bool:
    # Check if path is an existing directory on the local filesystem
    return os.path.isdir(path)

def is_http_url(parsed) -> bool:
    # Check if URL scheme is HTTP or HTTPS
    return parsed.scheme in ("http", "https")

# --- Local file and folder fetchers ---

def fetch_local_file(src: str) -> bytes:
    logger.info(f"Loading local file: {src}")
    try:
        # Archive a single local file given by path and return bytes
        return archive_file_from_path(src)
    except Exception as e:
        logger.error(f"Failed to read local file '{src}': {e}")
        raise

def fetch_local_folder(src: str) -> bytes:
    logger.info(f"Archiving local folder: {src}")
    # Archive the entire local folder and return bytes
    return archive_folder(src)

# --- HTTP URL fetcher ---

def fetch_http_url(src: str) -> bytes:
    logger.info(f"Downloading from URL: {src}")
    try:
        # Perform a GET request with a timeout
        response = requests.get(src, timeout=10)
        response.raise_for_status()
        # Use the last part of URL path as archive filename or fallback
        arcname = os.path.basename(urlparse(src).path) or "downloaded_file"
        # Archive the downloaded content with the given filename
        return archive_file(response.content, arcname)
    except requests.RequestException as e:
        logger.error(f"HTTP request failed: {e}")
        raise

# --- Git repository fetch using shell git commands ---

def fetch_git_shell_repo(
    src: str,
    verbose: bool = False,
    allow_username_in_path: bool = False,
    temp_path: str = None,
    branch: str = None,
    subdir: str = None,
    depth: int = 2,
    token: str = None,
) -> bytes:
    logger.info(f"Cloning Git repository: {src} (branch: {branch}, depth: {depth})")

    # If a GitHub token is provided and URL is HTTPS GitHub, inject token for auth
    if token and "github.com" in src and src.startswith("https://"):
        parsed = urlparse(src)
        src = f"https://{token}@{parsed.netloc}{parsed.path}"

    # Create a secure temporary directory to clone the repo
    with SecureTemporaryDirectory(
        verbose=verbose,
        check_username_in_path=not allow_username_in_path,
        root_base=temp_path,
    ) as tmp:
        try:
            # Build git clone command with optional depth and branch parameters
            cmd = ["git", "clone"]
            if depth:
                cmd += ["--depth", str(depth)]
            if branch:
                cmd += ["--branch", branch]
            cmd += [src, tmp]

            # Run the git clone command
            subprocess.run(
                cmd, check=True
            )
            logger.info(f"Successfully cloned {src} into {tmp}")
        except subprocess.CalledProcessError as e:
            # Git clone failed; raise a RuntimeError with a message
            raise RuntimeError(f"Git clone failed") from e

        # Archive the cloned repository folder, optionally only a subdirectory
        return archive_folder(tmp, subdir=subdir)

# --- Fetch GitHub repo via the GitHub API ---

def fetch_github_api_repo(
    repo_path: str,
    token: str = None,
    branch: str = None,
    subdir: str = None,
    verbose: bool = False,
) -> bytes:
    branch = branch or "HEAD"
    logger.info(f"Fetching GitHub repo via API: {repo_path}@{branch}")

    # GitHub API URL to get the repository tree recursively
    api_url = f"https://api.github.com/repos/{repo_path}/git/trees/{branch}?recursive=1"
    headers = {"Authorization": f"token {token}"} if token else {}

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"GitHub API error {response.status_code}: {response.text}")

    # Log rate limit info if verbose
    rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
    rate_limit_limit = response.headers.get("X-RateLimit-Limit")
    if verbose and rate_limit_remaining is not None:
        logger.info(f"GitHub API rate limit: {rate_limit_remaining}/{rate_limit_limit}")

    data = response.json()

    if data.get("truncated"):
        # If the tree response is truncated, suggest using the git shell method
        raise RuntimeError("GitHub API response truncated — consider using git_shell=True")

    tree = data.get("tree", [])
    if not tree:
        raise RuntimeError("Repository tree is empty")

    file_dict = {}

    for entry in tree:
        # Only process files (blobs), ignore directories and others
        if entry.get("type") != "blob":
            continue

        file_path = PurePosixPath(entry["path"])
        if subdir:
            try:
                # If subdir is specified, check if file is inside subdir
                subdir_path = PurePosixPath(subdir.strip("/"))
                relative_path = file_path.relative_to(subdir_path)
            except ValueError:
                # Skip files not in the specified subdir
                continue
        else:
            relative_path = file_path

        # Skip unsafe paths for security
        if not is_safe_path("", str(relative_path)):
            logger.warning(f"Skipping unsafe path: {relative_path}")
            continue

        # Construct raw content URL for the file
        raw_url = f"https://raw.githubusercontent.com/{repo_path}/{branch}/{entry['path']}"
        logger.debug(f"Downloading file: {raw_url}")

        file_response = requests.get(raw_url)
        if file_response.status_code != 200:
            logger.warning(f"Skipping file '{entry['path']}' due to HTTP {file_response.status_code}")
            continue

        # Add file content to dictionary with relative path as key
        file_dict[str(relative_path)] = file_response.content

    if verbose:
        logger.info(f"Fetched {len(file_dict)} files.")

    # Archive all fetched files together and return bytes
    return archive_multiple_files(file_dict)

# --- Main fetch function that determines the source type and fetches accordingly ---

def fetch_source(
    src: str,
    token: str = None,
    verbose: bool = False,
    allow_username_in_path: bool = False,
    temp_path: str = None,
    git_shell: bool = False,
    branch: str = None,
    subdir: str = None,
    depth: int = 2,
) -> bytes:

    try:
        # Check if source is a local file
        if is_local_file(src):
            return fetch_local_file(src)

        # Check if source is a local folder
        if is_local_folder(src):
            return fetch_local_folder(src)

        # Try to parse the source as a git URL
        giturl = parse_git_url(src, allow_plain_resources=["github.com", "gitlab.com"])
        if giturl != None:
            # For GitHub HTTPS plain URLs and when not forcing git shell, use GitHub API
            if not git_shell and giturl.resource == 'github.com' and (giturl.type == 'https_plain' or giturl.type == 'domain_plain' or giturl.type == 'github_short' or giturl.type == 'github_path'):
                return fetch_github_api_repo(
                    f'{giturl.user}/{giturl.repo}',
                    token=token,
                    verbose=verbose,
                    branch=branch,
                    subdir=subdir,
                )
            else:
                # Determine the appropriate git URL to clone
                if giturl.type == 'https_plain':
                    url = src + '.git'
                elif giturl.type == 'domain_plain':
                    url = 'https://' + src + '.git'
                elif giturl.type == 'domain_git':
                    url = 'https://' + src
                elif giturl.type == 'github_short' or giturl.type == "github_path":
                    url = f'git@{giturl.resource}:{giturl.user}/{giturl.repo}.git'
                else:
                    url = src
                
                # Fetch the repo by cloning via git shell
                return fetch_git_shell_repo(
                    url,
                    verbose=verbose,
                    allow_username_in_path=allow_username_in_path,
                    temp_path=temp_path,
                    branch=branch,
                    subdir=subdir,
                    depth=depth,
                    token=token,
                )
        
        # If source is an HTTP URL, fetch via HTTP
        parsed = urlparse(src)
        if parsed and is_http_url(parsed):
            return fetch_http_url(src)

        # If none of the above, raise an error
        raise RuntimeError(f"Unsupported source format: {src}")

    except Exception as e:
        # Log the error with details if verbose, then re-raise
        log_error(f"Failed to fetch source '{src}'", e, verbose)
        raise

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]+', '_', name)

def get_output_filename(src: str, subdir: str = None) -> str:
    if is_local_file(src):
        return Path(src).name

    if is_local_folder(src):
        folder_name = Path(src).name
        if subdir and subdir.strip():
            folder_name += f"_{subdir.replace('/', '_')}"
        return folder_name

    giturl = parse_git_url(src, allow_plain_resources=["github.com", "gitlab.com"])
    if giturl:
        base_name = giturl.repo or "repo"
        if giturl.user:
            base_name = f"{giturl.user}_{base_name}"
        if subdir and subdir.strip():
            base_name += f"_{subdir.replace('/', '_')}"
        return base_name

    parsed = urlparse(src)
    if parsed.scheme in ("http", "https"):
        filename = Path(parsed.path).name
        if not filename:
            filename = "downloaded_file"
        return filename

    safe_name = sanitize_filename(src)
    if subdir and subdir.strip():
        safe_name += f"_{sanitize_filename(subdir)}"
    return safe_name