import os
import shutil
import tempfile
import secrets
import time
import stat
import getpass
import platform
from pathlib import Path

def get_system_drive() -> str:
    """Return Windows system drive (e.g. 'C:/') or fallback 'C:/'."""
    drive = os.environ.get('SYSTEMDRIVE')
    if drive and len(drive) == 2 and drive[1] == ':':
        return drive + '/'
    return 'C:/'

def path_contains_username(path: Path) -> bool:
    """Check if path contains current username (case-insensitive)."""
    username = getpass.getuser().lower()
    return username in str(path).lower()

def select_root_base(verbose: bool = False) -> Path:
    """Select the best root directory for temp data with priority and checks."""
    username = getpass.getuser().lower()
    candidates = []

    if platform.system() == "Windows":
        # Try RAM disk first (R:/)
        candidates.append(Path("R:/"))

    # Add current working directory if safe
    cwd = Path.cwd()
    if not path_contains_username(cwd):
        candidates.append(cwd)

    if platform.system() == "Windows":
        # Then system drive (C:/ or dynamic)
        system_drive = get_system_drive()
        candidates.append(Path(system_drive))
    else:
        # Unix-like system tmp
        candidates.append(Path("/tmp"))

    for candidate in candidates:
        if path_contains_username(candidate):
            if verbose:
                print(f"Skipping {candidate} because it contains username.")
            continue

        try:
            test_path = candidate / f"permtest-{secrets.token_hex(4)}"
            test_path.mkdir(parents=True, exist_ok=False)
            test_path.rmdir()
            if verbose:
                print(f"Using root base directory: {candidate}")
            return candidate
        except Exception as e:
            if verbose:
                print(f"Cannot write to {candidate} ({e}), trying next candidate...")

    # Final fallback to system temp dir
    fallback = Path(tempfile.gettempdir())
    if verbose:
        print(f"Falling back to system temp directory: {fallback}")
    return fallback


class SecureTemporaryDirectory:
    def __init__(
        self,
        passes: int = 3,
        max_delete_retries: int = 5,
        verbose: bool = True,
        root_base: Path = None,
        min_depth: int = 2,
        max_depth: int = 5,
        min_files_per_dir: int = 2,
        max_files_per_dir: int = 4,
        max_file_size: int = 1024,  # max dummy file size in bytes
        check_username_in_path: bool = True  # safer default: enabled
    ):
        self._passes = passes
        self._max_retries = max_delete_retries
        self._verbose = verbose
        self._min_depth = min_depth
        self._max_depth = max_depth
        self._min_files = min_files_per_dir
        self._max_files = max_files_per_dir
        self._max_file_size = max_file_size
        self._check_username_in_path = check_username_in_path

        # Select root base if not provided
        if root_base is None:
            root_base = select_root_base(verbose=self._verbose)

        # Create unique session root directory with retries
        self._session_root = None
        for _ in range(10):
            candidate = root_base / f"tmp-{secrets.token_hex(8)}"
            if not candidate.exists():
                try:
                    candidate.mkdir(parents=True, exist_ok=False)
                    self._session_root = candidate
                    break
                except Exception as e:
                    if self._verbose:
                        print(f"Failed to create session root: {candidate}: {e}")
        if self._session_root is None:
            raise RuntimeError("Failed to create unique session root directory after 10 attempts.")

        # Create main temp directory inside session root
        self._path = self._session_root / f"tmp-{secrets.token_hex(8)}"
        self._path.mkdir(parents=True, exist_ok=False)

        # Check username in path if enabled, abort if found
        if self._check_username_in_path and path_contains_username(self._path):
            raise RuntimeError(f"Temporary path '{self._path}' contains username — aborting.")

        self._closed = False

        # Create randomized directory/file structure and wipe once on start
        self._mangle_structure()
        self._secure_wipe(self._path)

    def __enter__(self):
        return str(self._path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def cleanup(self):
        if self._closed:
            return
        try:
            self._secure_wipe(self._path)
            self._mangle_structure()
            self._secure_wipe(self._path)
            shutil.rmtree(self._session_root, onerror=self._on_rm_error)
        finally:
            self._closed = True

    def _secure_wipe(self, directory: Path):
        """Securely overwrite all files and rename/remove files and directories."""
        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                filepath = Path(root) / name
                self._overwrite_file(filepath)
                filepath = self._overwrite_filename(filepath)
                self._retry_remove(filepath)

            for name in dirs:
                dirpath = Path(root) / name
                dirpath = self._overwrite_filename(dirpath)
                self._retry_remove(dirpath, is_dir=True)

    def _overwrite_file(self, filepath: Path):
        """Overwrite a file with multiple passes using different patterns."""
        try:
            length = filepath.stat().st_size
            filepath.chmod(0o600)
            block_size = 4096
            with open(filepath, "r+b") as f:
                for i in range(self._passes):
                    f.seek(0)
                    bytes_remaining = length
                    while bytes_remaining > 0:
                        chunk_size = min(block_size, bytes_remaining)
                        pattern = self._get_pattern(i, chunk_size)
                        f.write(pattern)
                        bytes_remaining -= chunk_size
                    f.flush()
                    try:
                        os.fsync(f.fileno())
                    except OSError as e:
                        if self._verbose:
                            print(f"fsync() failed for {filepath}: {e}")
        except Exception as e:
            if self._verbose:
                print(f"Error overwriting file {filepath}: {e}")

    def _get_pattern(self, pass_num: int, length: int) -> bytes:
        """Return pattern to write: zeros, ones, or random bytes cycling by pass."""
        if pass_num % 3 == 0:
            return b"\x00" * length
        elif pass_num % 3 == 1:
            return b"\xFF" * length
        else:
            return secrets.token_bytes(length)

    def _overwrite_filename(self, path: Path, passes: int = 3):
        """Rename file or directory multiple times with random names of same length."""
        for _ in range(passes):
            try:
                random_name = ''.join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(len(path.name)))
                new_path = path.with_name(random_name)
                path.rename(new_path)
                path = new_path
            except Exception as e:
                if self._verbose:
                    print(f"Failed to overwrite filename {path}: {e}")
                break
        return path

    def _retry_remove(self, path: Path, is_dir=False):
        """Retry deletion with incremental delays and permission fixes."""
        for attempt in range(self._max_retries):
            try:
                if is_dir:
                    path.rmdir()
                else:
                    path.unlink()
                return
            except FileNotFoundError:
                return
            except Exception as e:
                if self._verbose:
                    print(f"Retry {attempt+1}/{self._max_retries} failed deleting {path}: {e}")
                time.sleep(0.1 * (attempt + 1))

        if self._verbose:
            print(f"Failed to delete {path} after {self._max_retries} attempts.")

    def _mangle_structure(self):
        """Create random nested directories and files with random content."""
        depth = secrets.randbelow(self._max_depth - self._min_depth + 1) + self._min_depth
        current = self._path
        for _ in range(depth):
            subdir_name = ''.join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(8 + secrets.randbelow(4)))
            current = current / subdir_name
            current.mkdir(exist_ok=True)

            num_files = secrets.randbelow(self._max_files - self._min_files + 1) + self._min_files
            for _ in range(num_files):
                filename = ''.join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(10 + secrets.randbelow(4)))
                file_path = current / filename
                size = secrets.randbelow(self._max_file_size - 128 + 1) + 128
                with open(file_path, "wb") as f:
                    f.write(secrets.token_bytes(size))

    def _on_rm_error(self, func, path, exc_info):
        """Error handler for shutil.rmtree: fixes permissions and retries deletion."""
        if not os.access(path, os.W_OK):
            try:
                os.chmod(path, stat.S_IWUSR)
                func(path)
            except Exception as e:
                if self._verbose:
                    print(f"Failed to fix permissions and delete {path}: {e}")
        else:
            if self._verbose:
                print(f"Unhandled error deleting {path}, skipping.")