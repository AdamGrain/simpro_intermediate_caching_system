# ── Session logging ────────────────────────────────────────────────────────────

from datetime import datetime
from pathlib import Path
import sys
from typing import Any

class _Tee:
    # Replaces sys.stdout/stderr so every write — including subprocess output
    # piped through Python — goes to both the terminal and the log file.
    # logging.FileHandler only captures explicit logging.* calls; it cannot
    # intercept subprocess stdout or bare print() calls written to sys.stdout.
    def __init__(self, original: Any, file_handle: Any) -> None:
        self._original = original
        self._file = file_handle

    def write(self, s: str) -> int:
        self._original.write(s)
        self._file.write(s)
        return len(s)

    def flush(self) -> None:
        self._original.flush()
        self._file.flush()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._original, name)


def setup_logging(log_dir: Path) -> Path:
    """Create a timestamped log file and tee all stdout/stderr output to it.

    Returns the path of the created log file.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"build_{ts}.log"
    fh = open(log_path, "w", encoding="utf-8", buffering=1)
    sys.stdout = _Tee(sys.stdout, fh)
    sys.stderr = _Tee(sys.stderr, fh)
    return log_path
