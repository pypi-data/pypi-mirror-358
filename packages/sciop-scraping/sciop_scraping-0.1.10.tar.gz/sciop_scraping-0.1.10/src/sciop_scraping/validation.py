"""
Helper methods for validation that might be used in multiple quests
"""

import hashlib
import re
from pathlib import Path
from typing import TYPE_CHECKING

from tqdm import tqdm

if TYPE_CHECKING:
    from sciop_scraping.quests.base import ValidationError


def validate_bagit_manifest(
    path: Path, hash_type: str = "md5", remove: bool = False, hash_when_missing: bool = True
) -> list["ValidationError"]:
    """
    Given the base directory of a bagit directory that contains `manifest-{hash_type}.txt`
    and `data/` check the files against the manifest,
    returning ValidationErrors for missing or incorrect files.

    Args:
        path (Path): bagit directory
        hash_type (str): string name of hash algo,
            should match the file name abbreviation and be available by that name in hashlib
        remove (bool): If ``True``, remove invalid files (default False)
        hash_when_missing (bool): If ``False``, when files are missing, skip hash checking.
            If ``True``, hash files even if some are missing
    """
    from sciop_scraping.quests.base import ValidationError

    errors = []
    path = Path(path)
    manifest_path = path / f"manifest-{hash_type}.txt"

    if not manifest_path.exists():
        errors.append(
            ValidationError(
                type="manifest",
                path=manifest_path,
                msg="No manifest file found at expected location!",
            )
        )
        return errors

    with open(manifest_path) as f:
        manifest = f.read()

    lines = manifest.splitlines()
    # split into (hash, path) pairs
    items = [re.split(r"\s+", line.strip(), maxsplit=1) for line in lines]

    # first check for missing files, we know we're invalid if we have missing files
    # and can quit early
    for item in tqdm(items, desc="Checking for missing files"):
        expected_hash, sub_path = item
        abs_path = path / sub_path
        if not abs_path.exists():
            errors.append(ValidationError(type="missing", path=sub_path, msg="File not found"))

    if not hash_when_missing and len(errors) > 0:
        return errors

    for item in tqdm(items, desc="Validating file hashes"):
        expected_hash, sub_path = item
        abs_path = path / sub_path
        with open(abs_path, "rb") as f:
            file_hash = hashlib.file_digest(f, hash_type).hexdigest()

        if file_hash != expected_hash:
            errors.append(ValidationError(type="incorrect", path=sub_path, msg="Hash mismatch"))
            if remove:
                abs_path.unlink()
    return errors
