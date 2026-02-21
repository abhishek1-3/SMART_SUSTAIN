# ──────────────────────────────────────────────
#  SMART_SUSTAIN  —  app.py
#  Main Streamlit entry point
#  Run: streamlit run app.py
# ──────────────────────────────────────────────

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from config import APP_TITLE, APP_ICON, APP_VERSION, MODULES, SDG_WEIGHTS
from utils import composite_score
from modules.education import EducationModule
from modules.employment import EmploymentModule     
from modules.environment import EnvironmentModule
from modules.health import HealthModule
from modules.smart_city import SmartCityModule

# ── Page config ────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Module registry ────────────────────────────
MODULE_CLASSES = {
    "education":   EducationModule,
    "employment":  EmploymentModule,
    "environment": EnvironmentModule,
    "health":      HealthModule,
    "smart_city":  SmartCityModule,
}

# ── Session state: cache module instances ──────
for key, cls in MODULE_CLASSES.items():
    if key not in st.session_state:
        st.session_state[key] = cls()

# ── Sidebar ────────────────────────────────────
with st.sidebar:
    st.title(f"{APP_ICON} SMART_SUSTAIN")
    st.caption(f"v{APP_VERSION}")
    st.divider()

    page = st.radio(
        "Navigate",
        options=["🖼️ Dashboard"] + [v["label"] for v in MODULES.values()],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("© AI POWERED SMART SUSTAIN")
    st.caption("Data sources: City DB, Open Data Portals, APIs")
    st.caption("For feedback or contributions, visit our GitHub repo.")
    st.caption("Developed by ABHISHEK KUMAR ")
# ── Map sidebar label → module key ─────────────
label_to_key = {v["label"]: k for k, v in MODULES.items()}


# ── Dashboard page ─────────────────────────────
def render_dashboard():
    st.title(f"{APP_ICON} Smart City Analytics Dashboard")
    st.markdown("A comprehensive overview of city performance across key sustainability domains.")
    st.divider()

    scores: dict[str, float] = {}
    cols = st.columns(len(MODULE_CLASSES))

    for col, (key, cls_instance) in zip(cols, st.session_state.items()):
        if key not in MODULE_CLASSES:
            continue
        try:
            score = cls_instance.run()
        except Exception as exc:
            score = 0.0
            st.warning(f"Could not load {key}: {exc}")
        scores[key] = score
        col.metric(
            label=MODULES[key]["label"],
            value=f"{score:.1f}",
            delta=None,
        )

    st.divider()

    # Composite score
    if scores:
        city_score = composite_score(scores, SDG_WEIGHTS)
        st.subheader("🏅 Overall City Score")
        progress_val = city_score / 100
        st.progress(progress_val)
        st.metric("Composite Sustainability Score", f"{city_score:.1f} / 100")

    # Score bar chart
    if scores:
        import pandas as pd
        score_df = pd.DataFrame(
            {"Module": list(scores.keys()), "Score": list(scores.values())}
        ).set_index("Module")
        st.subheader("Domain Scores")
        st.bar_chart(score_df)


# ── Routing ────────────────────────────────────
if page == "🖼️ Dashboard":
    render_dashboard()
else:
    module_key = label_to_key.get(page)
    if module_key:
        module_instance = st.session_state[module_key]
        if module_instance.data is None:
            with st.spinner("Loading data …"):
                try:
                    module_instance.run()
                except Exception as exc:
                    st.error(f"Failed to load data: {exc}")
        module_instance.render()
    else:
        st.error("Page not found.")