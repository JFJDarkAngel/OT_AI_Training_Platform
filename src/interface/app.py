from textwrap import dedent

import streamlit as st
from streamlit_option_menu import option_menu

from src.interface.home_page import show_home_page
from src.interface.new_scenario_page import (
    show_new_scenario_page,
)
from src.interface.scenario_history_page import (
    show_scenario_history_page,
)


st.set_page_config(
    page_title="OT AI Training & Evaluation Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGES = [
    "Home",
    "New Scenario",
    "Scenario History",
    "About",
]


PAGE_ICONS = [
    "house-door",
    "file-earmark-plus",
    "folder2-open",
    "info-circle",
]


if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"


if st.session_state["current_page"] not in PAGES:
    st.session_state["current_page"] = "Home"


st.markdown(
    dedent(
        """
        <style>
        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #102d50 0%,
                    #071a30 100%
                );
        }

        [data-testid="stSidebarContent"] {
            padding-top: 0.8rem;
        }

        .sidebar-brand {
            text-align: center;
            padding: 1rem 0 1.7rem 0;
        }

        .sidebar-logo {
            width: 74px;
            height: 74px;
            margin: 0 auto 0.75rem auto;
            border-radius: 20px;
            background:
                linear-gradient(
                    145deg,
                    #2f7de1,
                    #1352aa
                );
            border:
                3px solid
                rgba(255, 255, 255, 0.85);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 2rem;
            font-weight: 800;
            box-shadow:
                0 10px 25px
                rgba(0, 0, 0, 0.22);
        }

        .sidebar-title {
            font-size: 1.2rem;
            font-weight: 800;
            color: #ffffff;
        }

        .sidebar-subtitle {
            margin-top: 0.25rem;
            color: #9fb4d0;
            font-size: 0.78rem;
        }

        [data-testid="stSidebar"] hr {
            border-color:
                rgba(255, 255, 255, 0.12);
        }
        </style>
        """
    ),
    unsafe_allow_html=True,
)


with st.sidebar:
    brand_html = (
        '<div class="sidebar-brand">'
        '<div class="sidebar-logo">OT</div>'
        '<div class="sidebar-title">'
        'OT AI Platform'
        '</div>'
        '<div class="sidebar-subtitle">'
        'Training &amp; Evaluation'
        '</div>'
        '</div>'
    )

    st.markdown(
        brand_html,
        unsafe_allow_html=True,
    )

    selected_page = option_menu(
        menu_title=None,
        options=PAGES,
        icons=PAGE_ICONS,
        default_index=PAGES.index(
            st.session_state["current_page"]
        ),
        orientation="vertical",
        key="main_navigation",
        styles={
            "container": {
                "padding": "0",
                "background-color": "transparent",
            },
            "icon": {
                "color": "#dbeafe",
                "font-size": "19px",
            },
            "nav-link": {
                "font-size": "15px",
                "font-weight": "600",
                "text-align": "left",
                "margin": "5px 0",
                "padding": "12px 14px",
                "border-radius": "10px",
                "color": "#eaf2ff",
                "--hover-color":
                    "rgba(39, 104, 217, 0.28)",
            },
            "nav-link-selected": {
                "background":
                    "linear-gradient("
                    "135deg, #2768d9, #174caf"
                    ")",
                "color": "#ffffff",
                "box-shadow":
                    "0 7px 18px "
                    "rgba(21, 78, 177, 0.35)",
            },
        },
    )

    if (
        selected_page
        != st.session_state["current_page"]
    ):
        st.session_state["current_page"] = (
            selected_page
        )

        if selected_page == "Scenario History":
            st.session_state[
                "scenario_history_view"
            ] = "list"

    st.markdown("---")

    st.caption(
        "Secure · Intelligent · Resilient"
    )


if selected_page == "Home":
    show_home_page()

elif selected_page == "New Scenario":
    show_new_scenario_page()

elif selected_page == "Scenario History":
    show_scenario_history_page()

elif selected_page == "About":
    st.title("About")

    st.write(
        "OT AI Training & Evaluation Platform "
        "for industrial incident-response training."
    )