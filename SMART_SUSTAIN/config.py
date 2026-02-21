# ──────────────────────────────────────────────
#  SMART_SUSTAIN  —  config.py
#  Global constants, SDG weights, and paths
# ──────────────────────────────────────────────

import os
from pathlib import Path

# ── Paths ──────────────────────────────────────
BASE_DIR        = Path(__file__).resolve().parent
DATA_RAW_DIR    = BASE_DIR / "data" / "raw"
DATA_PROC_DIR   = BASE_DIR / "data" / "processed"
MODEL_SAVE_DIR  = BASE_DIR / "models" / "saved"

# Auto-create directories if they don't exist
for _dir in [DATA_RAW_DIR, DATA_PROC_DIR, MODEL_SAVE_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)

# ── Database ───────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME", "smart_sustain"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root212"),
}

# ── App ────────────────────────────────────────
APP_TITLE   = "SMART_SUSTAIN — Smart City Analytics"
APP_ICON    = "🌆"
APP_VERSION = "1.0.0"

# ── Module registry  ───────────────────────────
#  Key  : used internally and as URL page param
#  Label: shown in the UI sidebar
MODULES = {
    "education":   {"label": "📚 Education",   "icon": "📚"},
    "employment":  {"label": "💼 Employment",  "icon": "💼"},
    "environment": {"label": "🌿 Environment", "icon": "🌿"},
    "health":      {"label": "🏥 Health",      "icon": "🏥"},
    "smart_city":  {"label": "🏙️ Smart City",  "icon": "🏙️"},
}

# ── SDG Weights (0–1, must sum to 1.0) ────────
#  Adjust these to reflect your city's priorities
SDG_WEIGHTS = {
    "education":   0.20,
    "employment":  0.20,
    "environment": 0.20,
    "health":      0.20,
    "smart_city":  0.20,
}

assert abs(sum(SDG_WEIGHTS.values()) - 1.0) < 1e-6, \
    "SDG_WEIGHTS must sum to 1.0"

# ── ML ─────────────────────────────────────────
MODEL_FRAMEWORK = "tensorflow"   # "tensorflow" | "sklearn"
DEFAULT_EPOCHS  = 50
DEFAULT_BATCH   = 32
RANDOM_SEED     = 42