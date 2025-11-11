"""Utility helpers used across the solo mining calculator."""

from __future__ import annotations

import logging
import math
import os
import pickle
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

# Determine paths relative to the project root so imports work from anywhere.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "Output"
LOG_PATH = OUTPUT_DIR / "logs" / "app.log"


def _ensure_logging_setup() -> logging.Logger:
    """Create a simple logger that writes to stdout and the app log file."""
    logger = logging.getLogger("solo_mining")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Make sure the log directory exists before writing.
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False

    logger.info("Logging initialized at %s", LOG_PATH)
    return logger


LOGGER = _ensure_logging_setup()


def read_csv(path: os.PathLike | str, **kwargs: Any) -> Optional[pd.DataFrame]:
    """Read a CSV file into a DataFrame, logging any errors."""
    try:
        LOGGER.info("Reading CSV: %s", path)
        return pd.read_csv(path, **kwargs)
    except Exception as exc:  # Broad catch to keep the app simple for beginners.
        LOGGER.error("Failed to read CSV %s: %s", path, exc)
        print(f"Error reading CSV {path}: {exc}")
    return None


def write_csv(df: pd.DataFrame, path: os.PathLike | str, **kwargs: Any) -> bool:
    """Write a DataFrame to CSV with basic error handling."""
    try:
        LOGGER.info("Writing CSV: %s", path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False, **kwargs)
        return True
    except Exception as exc:
        LOGGER.error("Failed to write CSV %s: %s", path, exc)
        print(f"Error writing CSV {path}: {exc}")
    return False


def save_pickle(obj: Any, path: os.PathLike | str) -> bool:
    """Serialize a Python object to disk."""
    try:
        LOGGER.info("Saving pickle: %s", path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as fh:
            pickle.dump(obj, fh)
        return True
    except Exception as exc:
        LOGGER.error("Failed to save pickle %s: %s", path, exc)
        print(f"Error saving pickle {path}: {exc}")
    return False


def load_pickle(path: os.PathLike | str) -> Optional[Any]:
    """Load a pickled object from disk."""
    try:
        LOGGER.info("Loading pickle: %s", path)
        with open(path, "rb") as fh:
            return pickle.load(fh)
    except Exception as exc:
        LOGGER.error("Failed to load pickle %s: %s", path, exc)
        print(f"Error loading pickle {path}: {exc}")
    return None


def safe_eval(expr: str, variables_dict: Optional[Dict[str, Any]] = None) -> Any:
    """Evaluate math expressions safely using a limited namespace."""
    allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("_")}
    if variables_dict:
        allowed_names.update(variables_dict)

    try:
        LOGGER.info("Evaluating expression: %s", expr)
        return eval(expr, {"__builtins__": {}}, allowed_names)
    except Exception as exc:
        LOGGER.error("Failed to eval expression %s: %s", expr, exc)
        print(f"Error evaluating expression '{expr}': {exc}")
        return None
