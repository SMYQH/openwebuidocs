"""Local JSON artifacts must not overwrite their inputs or documentation."""

import json
import os
from pathlib import Path
import tempfile


def check_artifacts(outputs, inputs, protected_dirs) -> None:
    paths = [p.resolve() for p in outputs if p is not None]
    protected = {p.resolve() for p in inputs if p is not None}
    roots = [p.resolve() for p in protected_dirs]
    for path in paths:
        if path in protected or any(path.is_relative_to(root) for root in roots):
            raise ValueError("Output must not overwrite inputs, credentials, or documentation")
        if path.suffix.lower() != ".json" or path.is_dir():
            raise ValueError("Output must be a JSON file path")
        if any(other.is_relative_to(path) or path.is_relative_to(other) for other in protected):
            raise ValueError("Output paths must be distinct and may not contain other artifacts")
        protected.add(path)


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".translation-", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def save_bundle(path: Path, bundle: dict) -> None:
    atomic_write(path, (json.dumps(bundle, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
