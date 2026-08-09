import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.interface.styles import apply_global_styles
from src.interface.pages.dashboard import render_dashboard
from src.interface.pages.new_scenario import render_new_scenario
from src.interface.pages.hmi_visualization import render_hmi_visualization
from src.interface.pages.stakeholder_response import render_stakeholder_response
from src.interface.pages.evaluation import render_evaluation
from src.interface.pages.results import render_results
from src.interface.pages.scenario_history import render_scenario_history

st.set_page_config(
    page_title="AI OT Incident Response",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_global_styles()

if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"

page = st.session_state["page"]

if page == "new_scenario":
    render_new_scenario()
elif page == "hmi_visualization":
    render_hmi_visualization()
elif page == "stakeholder_response":
    render_stakeholder_response()
elif page == "evaluation":
    render_evaluation()
elif page == "results":
    render_results()
elif page == "scenario_history":
    render_scenario_history()
else:
    render_dashboard()
