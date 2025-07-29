import os
import io
import zipfile

from pathlib import Path

from secpack.logger import logger

def archive_folder(folder: str, subdir: str = None) -> bytes:
    buf = io.BytesIO()
    root = Path(folder).resolve()

    if subdir:
        root = root / subdir
        root = root.resolve()
        if not str(root).startswith(str(Path(folder).resolve())):
            raise ValueError("Invalid subdir path")

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, _, files in os.walk(root):
            for f in files:
                full_path = Path(path) / f
                arcname = str(full_path.relative_to(root))
                zf.write(str(full_path), arcname)
    logger.info(f"Folder '{folder}' archived successfully" + (f" (subdir: '{subdir}')" if subdir else ""))
    return buf.getvalue()


def archive_file(file_bytes: bytes, arcname: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(arcname, file_bytes)
    logger.info(f"File '{arcname}' archived successfully")
    return buf.getvalue()


def archive_file_from_path(filepath: str) -> bytes:
    with open(filepath, "rb") as f:
        return archive_file(f.read(), os.path.basename(filepath))

def archive_multiple_files(file_dict: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, content in file_dict.items():
            zf.writestr(arcname, content)
    logger.info(f"{len(file_dict)} files archived in memory")
    return buf.getvalue()

def extract_archive(data: bytes, target: str):
    with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
        zf.extractall(target)
    logger.info(f"Archive extracted to '{target}'")

def extract_single_file_from_zip(zip_bytes: bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        filelist = [f for f in zf.filelist if not f.is_dir()]
        if len(filelist) < 1:
            raise ValueError(f"Expected at least one file in archive, found {len(filelist)}")
        return zf.read(filelist[0].filename), filelist[0].filename