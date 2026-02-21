# ──────────────────────────────────────────────
#  SMART_SUSTAIN  —  utils.py
#  Database connections & shared math helpers
# ──────────────────────────────────────────────

import os
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import mysql.connector
import pandas as pd
import numpy as np
from dotenv import load_dotenv

from config import DB_CONFIG, SDG_WEIGHTS, MODEL_SAVE_DIR

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("smart_sustain.utils")


# ── Database ───────────────────────────────────

def get_connection() -> mysql.connector.MySQLConnection:
    """Return a raw MySQL connection. Caller is responsible for closing it."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as exc:
        logger.error("DB connection failed: %s", exc)
        raise


@contextmanager
def db_cursor(dictionary: bool = True):
    """
    Context manager that yields a cursor and auto-commits / rolls back.

    Usage::
        with db_cursor() as cur:
            cur.execute("SELECT * FROM cities")
            rows = cur.fetchall()
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=dictionary)
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def query_to_df(sql: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """Execute a SELECT query and return results as a DataFrame."""
    with db_cursor() as cur:
        cur.execute(sql, params or ())
        rows = cur.fetchall()
    return pd.DataFrame(rows)


def execute(sql: str, params: Optional[tuple] = None) -> int:
    """Execute an INSERT / UPDATE / DELETE and return rows affected."""
    with db_cursor() as cur:
        cur.execute(sql, params or ())
        return cur.rowcount


# ── Scoring / Math helpers ─────────────────────

def normalize(series: pd.Series, low: float = 0.0, high: float = 100.0) -> pd.Series:
    """Min-max normalize a series to [low, high]."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(np.full(len(series), (low + high) / 2), index=series.index)
    return low + (series - mn) / (mx - mn) * (high - low)


def composite_score(scores: dict[str, float],
                    weights: Optional[dict[str, float]] = None) -> float:
    """
    Weighted average of module scores.

    Args:
        scores:  {module_name: score_0_to_100}
        weights: override SDG_WEIGHTS if needed
    Returns:
        Composite float 0–100
    """
    w = weights or SDG_WEIGHTS
    total_w = sum(w[k] for k in scores if k in w)
    if total_w == 0:
        return 0.0
    return sum(scores[k] * w[k] for k in scores if k in w) / total_w


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Clamp a value to [lo, hi]."""
    return max(lo, min(hi, value))


# ── Model helpers ──────────────────────────────

def model_path(name: str, ext: str = "h5") -> Path:
    """Return the full path for a saved model file."""
    return MODEL_SAVE_DIR / f"{name}.{ext}"


def load_keras_model(name: str):
    """Load a saved Keras model by name (without extension)."""
    try:
        import tensorflow as tf  # noqa: PLC0415
        path = model_path(name, "h5")
        logger.info("Loading Keras model: %s", path)
        return tf.keras.models.load_model(str(path))
    except Exception as exc:
        logger.error("Failed to load model '%s': %s", name, exc)
        raise