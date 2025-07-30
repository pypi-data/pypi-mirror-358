import random
from pathlib import Path

import bagit
import pytest

from sciop_scraping.validation import validate_bagit_manifest


@pytest.mark.parametrize("algo", ["sha256", "sha512", "md5"])
def test_valid_bagit(tmp_bagit: bagit.Bag, algo: str):
    """a valid bagit archive should be valid..."""
    errors = validate_bagit_manifest(tmp_bagit.path, algo)
    assert len(errors) == 0


@pytest.mark.parametrize("algo", ["sha256", "sha512", "md5"])
def test_invalid_bagit(tmp_bagit: bagit.Bag, algo: str):
    """an invalid bagit archive should not be valid..."""
    path = Path(tmp_bagit.path)
    with open(path / "data" / "regular.txt", "wb") as f:
        f.write(random.randbytes(32 * (2**10)))

    errors = validate_bagit_manifest(tmp_bagit.path, algo)
    assert len(errors) == 1
    assert errors[0].path == Path("data/regular.txt")
    assert errors[0].type_ == "incorrect"
