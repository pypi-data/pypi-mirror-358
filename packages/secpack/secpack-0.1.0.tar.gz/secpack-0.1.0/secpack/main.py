import os
import io
import sys
import argparse
import subprocess
import zipfile

import getpass
from pathlib import Path

from secpack.logger import logger, log_error
from secpack.security import SecureTemporaryDirectory
from secpack.encryption import encrypt_data, decrypt_data
from secpack.hashing import verify_with_hash_file, make_hash_file
from secpack.archiving import archive_folder, extract_archive, extract_single_file_from_zip
from secpack.fetching import fetch_source, get_output_filename

# --- Password ---
def get_password(arg=None):
    if arg:
        return arg
    env = os.getenv("SECPACK_PASSWORD")
    if env:
        logger.info("Using password from environment variable")
        return env
    p = Path.home() / ".secpack_pass"
    if p.exists():
        logger.warning("Using password from ~/.secpack_pass file (make sure it's secure!)")
        return p.read_text().strip()
    return getpass.getpass("Enter password: ")


def run_start_script(folder: str, allow_execute: bool = False, extra_args=None):
    path = os.path.join(folder, "start.py")
    if not os.path.isfile(path):
        return

    logger.warning(f"Start script detected: {path}")

    if allow_execute:
        confirmed = True
    else:
        reply = input("Execute start.py? [y/N]: ").strip().lower()
        confirmed = reply == "y"

    if not confirmed:
        logger.info("Execution skipped by user")
        return

    logger.info("Executing start.py")
    try:
        cmd = [sys.executable, path]
        if extra_args:
            cmd.extend(extra_args)
        subprocess.run(cmd, check=True)
        logger.info("start.py executed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Execution failed: {e}")


def fetch_current_source(args):
    content = fetch_source(args.src, token=args.token, verbose=args.verbose,
                           allow_username_in_path=args.allow_username,
                           temp_path=args.temp_path, git_shell=args.git_shell, subdir=args.subdir, branch=args.branch, depth=args.depth)

    return content


# --- Common utilities ---
def encrypt_current_content(content: bytes, args):
    return encrypt_data(content, get_password(args.password), args.scrypt_n, args.scrypt_r, args.scrypt_p)

def decrypt_current_content(content: bytes, args):
    return decrypt_data(content, get_password(args.password), args.scrypt_n, args.scrypt_r, args.scrypt_p)

def encrypt_folder(folder: str, output_path: str, args):
    data = archive_folder(folder)
    encrypted_data = encrypt_current_content(data, args)
    Path(output_path).write_bytes(encrypted_data)

def fetch_and_decrypt_archive(args):
    content = fetch_current_source(args)
    content = decrypt_current_content(content, args)
    return content

# --- Decorator for commands to handle errors and logging ---
def command_wrapper(func):
    def wrapper(args):
        try:
            func(args)
        except Exception as e:
            log_error(f"{func.__name__} failed", e, getattr(args, "verbose", False))
            sys.exit(1)
    return wrapper

@command_wrapper
def cmd_fetch(args):
    content = fetch_current_source(args)
    output_path = args.output

    if args.decrypt:
        content = decrypt_current_content(content, args)
        logger.info(f"Content decrypted.")
    
    if not output_path:
        output_path = get_output_filename(args.src, args.subdir) + '.zip'

    output_path = Path(output_path)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    output_path.write_bytes(content)

    logger.info(f"Fetched Content saved to '{output_path}'")


# --- Commands ---
@command_wrapper
def cmd_encrypt(args):
    content = fetch_current_source(args)
    content, filename = extract_single_file_from_zip(content)
    content = encrypt_current_content(content, args)
    
    output_file = args.output
    if not output_file:
        output_file = get_output_filename(args.src, args.subdir) + '.secbin'
    
    Path(output_file).write_bytes(content)
    logger.info(f"encrypted and saved to '{output_file}'")

    if args.hash:
        make_hash_file(output_file, content, args.hash_alg, args.hash_file)

@command_wrapper
def cmd_decrypt(args):
    content = fetch_current_source(args)
    content, filename = extract_single_file_from_zip(content)

    if args.hash:
        verify_with_hash_file(args.hash_file, content, args.hash_alg, filename)

    content = decrypt_current_content(content, args)
    
    output_path = args.output or f"{get_output_filename(args.src, args.subdir)}.bin"
    Path(output_path).write_bytes(content)
    logger.info(f"Decrypted content saved to '{output_path}'")

@command_wrapper
def cmd_pack(args):
    content = fetch_current_source(args)
    content = encrypt_current_content(content, args)
    
    output_file = args.output
    if not output_file:
        output_file = f'{get_output_filename(args.src, args.subdir)}.secpack'
    
    # content already packed
    Path(output_file).write_bytes(content)
    logger.info(f"Archive encrypted and saved to '{output_file}'")

    if args.hash:
        make_hash_file(output_file, content, args.hash_alg, args.hash_file)


@command_wrapper
def cmd_unpack(args):
    content = fetch_current_source(args)
    content, filename = extract_single_file_from_zip(content)

    if args.hash:
        verify_with_hash_file(args.hash_file, content, args.hash_alg, filename)

    content = decrypt_current_content(content, args)
    
    folder_name = get_output_filename(args.src, args.subdir)
    os.makedirs(folder_name, exist_ok=True)
    
    extract_archive(content, folder_name)


@command_wrapper
def cmd_execute(args):
    content = fetch_current_source(args)
    
    if args.raw:
        logger.info("Treating source as raw (not encrypted), skipping decryption")
    else:
        content, filename = extract_single_file_from_zip(content)
        if args.hash:
            verify_with_hash_file(args.hash_file, content, args.hash_alg, filename)
        content = decrypt_current_content(content, args)

    with SecureTemporaryDirectory(verbose=args.verbose, check_username_in_path=not args.allow_username,
                                  root_base=args.temp_path) as tmp:
        extract_archive(content, tmp)

        if args.cmd:
            logger.info(f"Executing shell command inside {tmp}: {args.cmd}")
            try:
                subprocess.run(args.cmd, cwd=tmp, check=True, shell=True)
                logger.info("Command executed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"Command execution failed: {e}")
            return
        
        run_path = os.path.join(tmp, args.run_file or "start.py")
        
        if not os.path.isfile(run_path):
            logger.error(f"File to execute not found: {run_path}")
            return

        logger.info(f"Script detected: {run_path}")

        if args.allow_execute:
            confirmed = True
        else:
            reply = input(f"Execute {os.path.basename(run_path)}? [y/N]: ").strip().lower()
            confirmed = reply == "y"

        if not confirmed:
            logger.info("Execution skipped by user")
            return

        logger.info(f"Executing {os.path.basename(run_path)}")
        try:
            cmd = [sys.executable, run_path]
            if args.args:
                cmd.extend(args.args)
            subprocess.run(cmd, cwd=tmp, check=True)
            logger.info(f"{os.path.basename(run_path)} executed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Execution failed: {e}")


@command_wrapper
def cmd_install(args):
    content = fetch_current_source(args)
    
    if args.raw:
        logger.info("Treating source as raw (not encrypted), skipping decryption")
    else:
        content, filename = extract_single_file_from_zip(content)
        if args.hash:
            verify_with_hash_file(args.hash_file, content, args.hash_alg, filename)

        content = decrypt_current_content(content, args)

    with SecureTemporaryDirectory(verbose=args.verbose, check_username_in_path=not args.allow_username, root_base=args.temp_path) as tmp:
        extract_archive(content, tmp)

        logger.info("Installing package with pip")
        subprocess.run([sys.executable, "-m", "pip", "install", tmp], check=True)
        logger.info("Package installed successfully")


def main():
    parser = argparse.ArgumentParser(
        prog="secpack",
        description="Secure package encryption, decryption, fetching and installation tool"
    )
    
    def add_arguments(parser):
        parser.add_argument("--password", "-p", help="Password for encryption/decryption")
        parser.add_argument("--token", help="GitHub token for private repo access")
        parser.add_argument("--scrypt-n", type=int, default=2 ** 18, help="scrypt CPU/memory cost parameter")
        parser.add_argument("--scrypt-r", type=int, default=8, help="scrypt block size parameter")
        parser.add_argument("--scrypt-p", type=int, default=1, help="scrypt parallelization parameter")
        parser.add_argument("--verbose", action="store_true", help="Show debug logs")
        parser.add_argument("--allow-username", "-a", action="store_true", help="Allow username in temporary file paths")
        parser.add_argument("--temp-path", "-t", default=None, help="Manually specify the path to the temporary folder")

        parser.add_argument("--subdir", help="Subdir")
        parser.add_argument("--git-shell", action="store_true", help="Prefer use git shell command to fetch resources from .git")
        parser.add_argument("--branch", help="Specify branch for git")
        parser.add_argument("--depth", help="Specify depth for git")

        parser.add_argument("--hash", action="store_true", help="Enable hash generation/verification with default file")
        parser.add_argument("--hash-file", help="Path to hash file for verification or output")
        parser.add_argument("--hash-alg", help="Hash algorithm to use (default: sha256)")
        
         
    add_arguments(parser)

    subparsers = parser.add_subparsers(dest="cmd", required=True)

    p = subparsers.add_parser("fetch", help="Fetch source from local path, URL, or GitHub repo")
    p.add_argument("src", help="Source to fetch")
    p.add_argument("-o", "--output", help="Output path for downloaded file or folder")
    p.add_argument("--decrypt", action="store_true", help="Decrypt after fetching")
    p.set_defaults(func=cmd_fetch)
    add_arguments(p)
    
    p = subparsers.add_parser("encrypt", help="Fetch single file, encrypt")
    p.add_argument("src", help="Source to fetch")
    p.add_argument("-o", "--output", help="Output encrypted archive file")
    p.set_defaults(func=cmd_encrypt)
    add_arguments(p)
    
    p = subparsers.add_parser("decrypt", help="Fetch single file, decrypt")
    p.add_argument("src", help="Source to fetch")
    p.add_argument("-o", "--output", help="Output folder to extract files")
    p.set_defaults(func=cmd_decrypt)
    add_arguments(p)
    
    p = subparsers.add_parser("pack", help="Fetch, archive (if folder) and encrypt")
    p.add_argument("src", help="Source to fetch")
    p.add_argument("-o", "--output", help="Output encrypted archive file")
    p.set_defaults(func=cmd_pack)
    add_arguments(p)
    
    p = subparsers.add_parser("unpack", help="Fetch, decrypt, unarchive (if folder)")
    p.add_argument("src", help="Source to fetch")
    p.add_argument("-o", "--output", help="Output folder to extract files")
    p.set_defaults(func=cmd_unpack)
    add_arguments(p)
    
    p = subparsers.add_parser("execute", help="Fetch, decrypt and execute start.py if found")
    p.add_argument("src", help="Source to fetch")
    p.add_argument("-x", "--allow-execute", action="store_true", help="Automatically run start.py without confirmation")
    p.add_argument("-r", "--raw", action="store_true", help="Treat source as raw (not encrypted), skip decryption")
    p.add_argument("-f", "--run-file", help="Specify a file to run instead of start.py")
    p.add_argument("--args", nargs=argparse.REMAINDER, help="Arguments to pass to start.py")
    p.add_argument("-c", "--cmd", help="Execute arbitrary shell command in unpacked folder")

    p.set_defaults(func=cmd_execute)
    add_arguments(p)
    
    p = subparsers.add_parser("install", help="Fetch, decrypt and install Python package")
    p.add_argument("src", help="Source to fetch")
    p.add_argument("-r", "--raw", action="store_true", help="Treat source as raw (not encrypted), skip decryption")
    p.set_defaults(func=cmd_install)
    add_arguments(p)

    args = parser.parse_args()

    if args.hash or args.hash_file or args.hash_alg:
        args.hash = True

    if args.hash and not args.hash_alg:
        args.hash_alg = 'sha256'

    if args.verbose:
        import logging
        logger.setLevel(logging.DEBUG)

    args.func(args)


if __name__ == "__main__":
    main()