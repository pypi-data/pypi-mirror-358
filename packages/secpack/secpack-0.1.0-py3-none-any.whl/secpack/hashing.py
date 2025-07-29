import os
import hashlib

from secpack.logger import logger

def make_hash_str(content: bytes, hash_alg: str):
    h = hashlib.new(hash_alg)
    h.update(content)
    hash_str = h.hexdigest()
    return hash_str

def write_hash_file(filepath: str, hash_str: str, hash_alg: str, output_path: str = None):
    hash_file = output_path or f"{filepath}.{hash_alg}"
    with open(hash_file, "w") as f:
        f.write(f"{hash_str}  {os.path.basename(filepath)}\n")
    logger.info(f"{hash_alg} hash file saved to {hash_file}")

def read_hash_file(hash_file: str) -> tuple[str, str]:
    with open(hash_file, "r") as f:
        line = f.readline().strip()
        if "  " in line:
            hash_str, filename = line.split("  ", 1)
            return hash_str.strip(), filename.strip()
        raise ValueError("Invalid hash file format (expected 'HASH  filename')")

def make_hash_file(filepath: str, content: bytes, hash_alg: str, output_path: str | None = None):
    hash_str = make_hash_str(content, hash_alg)  
    write_hash_file(filepath, hash_str, hash_alg, output_path)

def verify_with_hash_file(filepath: str | None, content: bytes, hash_alg: str, content_file_name: str):
    hash_path = filepath or f"{content_file_name}.{hash_alg}"
    if not os.path.exists(hash_path):
        raise RuntimeError(f"Hash file {hash_path} not found")

    actual_hash = make_hash_str(content, hash_alg)
    expected_hash, _ = read_hash_file(hash_path)

    if actual_hash != expected_hash:
        raise ValueError(f"Hash mismatch: expected {expected_hash}, got {actual_hash}")

    logger.info("Hash verification succeeded")