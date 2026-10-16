"""Portable source provenance and explicit experiment subset selection."""

import hashlib
from pathlib import Path


def source_fingerprint(root: Path | None = None) -> str:
    """Hash source names and LF-normalized contents, without recording host paths."""
    root = root or Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*.py"), key=lambda item: item.relative_to(root).as_posix()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8") + b"\0")
        digest.update(path.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    return digest.hexdigest()


def select_cases(cases, split: str, pair_ids: str | None, limit: int):
    available = [case for case in cases if split == "all" or case.split == split]
    if pair_ids is not None:
        requested = [value.strip() for value in pair_ids.split(",")]
        if not all(requested) or len(set(requested)) != len(requested):
            raise ValueError("Pair IDs must be nonempty and unique")
        mapping = {case.id: case for case in available}
        if any(value not in mapping for value in requested):
            raise ValueError("Unknown pair ID or ID outside selected split")
        if len(requested) > limit:
            raise ValueError("Selected pair count exceeds --limit")
        available = [mapping[value] for value in requested]
    else:
        available = available[:limit]
    if not available:
        raise ValueError("No lab tasks selected")
    return available
