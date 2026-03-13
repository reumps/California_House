"""Shared components: CSS, data loading, constants — CALIPREDICT theme."""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.core.model_loader import load_artifacts

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA LOADING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@st.cache_data
def load_data():
    return pd.read_csv(ROOT / "data" / "raw" / "california_housing.csv")

@st.cache_data
def load_test_predictions():
    path = ROOT / "models" / "test_predictions.csv"
    if path.exists():
        return pd.read_csv(path)
    return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.jpg"

def show_logo():
    """Display logo in sidebar if file exists, otherwise show text brand."""
    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.sidebar.markdown("""
        <div style="text-align:center; padding: 0.5rem 0 1rem;">
            <span style="font-size:1.5rem; font-weight:800; color:#1E3A5F; letter-spacing:-0.02em;">
                CALI<span style="color:#D4872E;">PREDICT</span>
            </span><br>
            <span style="font-size:0.55rem; font-weight:500; color:#6B8299; letter-spacing:0.08em; text-transform:uppercase;">
                California Housing Analytics
            </span>
        </div>
        """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LABELS & COLORS — CALIPREDICT palette
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LABELS = {
    "MedInc": "Revenu median",
    "HouseAge": "Age du logement",
    "AveRooms": "Pieces (moy.)",
    "AveBedrms": "Chambres (moy.)",
    "Population": "Population",
    "AveOccup": "Occupants (moy.)",
    "Latitude": "Latitude",
    "Longitude": "Longitude",
    "MedHouseVal": "Prix median",
}

COLUMN_DESCRIPTIONS = {
    "MedInc": "Revenu median des menages du district (en dizaines de milliers de dollars)",
    "HouseAge": "Age median des logements du district (en annees)",
    "AveRooms": "Nombre moyen de pieces par logement",
    "AveBedrms": "Nombre moyen de chambres par logement",
    "Population": "Population totale du district",
    "AveOccup": "Nombre moyen d'occupants par logement",
    "Latitude": "Latitude geographique du centre du district",
    "Longitude": "Longitude geographique du centre du district",
    "MedHouseVal": "Prix median des logements du district (en centaines de milliers de dollars)",
}

# Navy (#1E3A5F) + Orange (#D4872E) from CALIPREDICT logo
C = {
    "primary": "#1E3A5F",       # navy — main brand
    "secondary": "#D4872E",     # orange — accent
    "accent_light": "#F0A04B",  # light orange
    "success": "#2E8B57",       # sea green
    "danger": "#C0392B",        # crimson
    "warning": "#D4872E",       # orange (same as secondary)
    "muted": "#7A8FA6",         # blue-gray
    "navy_light": "#2C5282",    # lighter navy for gradients
    "navy_dark": "#152A43",     # darker navy
}

PL = dict(
    font=dict(family="Inter, -apple-system, sans-serif", color="#1E3A5F", size=12),
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=48, r=24, t=48, b=40),
    title_font=dict(size=14, color="#1E3A5F", family="Inter, sans-serif"),
    xaxis=dict(gridcolor="#E8ECF1", zeroline=False, linecolor="#CBD5E0"),
    yaxis=dict(gridcolor="#E8ECF1", zeroline=False, linecolor="#CBD5E0"),
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS — CALIPREDICT theme
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        #MainMenu, footer { visibility: hidden; }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #FFFFFF 0%, #F5F7FA 100%);
            border-right: 2px solid #D4872E;
        }

        /* ── Metrics cards — navy border accent ── */
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #CBD5E0;
            border-left: 4px solid #D4872E;
            border-radius: 10px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 1px 3px rgba(30,58,95,0.06);
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
        }
        [data-testid="stMetric"]:hover {
            box-shadow: 0 4px 14px rgba(30,58,95,0.1);
            border-left-color: #1E3A5F;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.78rem; font-weight: 600; color: #7A8FA6;
            text-transform: uppercase; letter-spacing: 0.04em;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.75rem; font-weight: 700; color: #1E3A5F;
        }

        /* ── Charts ── */
        [data-testid="stPlotlyChart"] > div {
            border: 1px solid #CBD5E0;
            border-radius: 12px;
            box-shadow: 0 1px 4px rgba(30,58,95,0.05);
            overflow: hidden;
            background: #FFFFFF;
        }

        /* ── Expanders ── */
        [data-testid="stExpander"] {
            border: 1px solid #CBD5E0;
            border-radius: 10px;
            box-shadow: 0 1px 2px rgba(30,58,95,0.04);
        }

        /* ── Section labels ── */
        .section-label {
            font-size: 0.68rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.07em;
            color: #D4872E; margin-bottom: 0.5rem;
        }

        /* ── Info boxes — navy tint ── */
        .info-box {
            background: linear-gradient(135deg, #EBF0F7 0%, #F5F7FA 100%);
            border: 1px solid #B0C4DB;
            border-left: 4px solid #1E3A5F;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 0.85rem;
            color: #1E3A5F;
            margin: 1rem 0;
        }

        /* ── Hero result card (Prediction page) ── */
        .hero-result {
            text-align: center;
            padding: 2.5rem 2rem;
            background: linear-gradient(135deg, #EBF0F7 0%, #FFF7ED 50%, #FEF3E2 100%);
            border: 2px solid #D4872E;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(212,135,46,0.12);
            margin: 1rem 0 1.5rem;
        }
        .hero-result .label {
            font-size: 0.85rem; font-weight: 500; color: #7A8FA6; margin-bottom: 0.25rem;
        }
        .hero-result .price {
            font-size: 3.25rem; font-weight: 800; color: #1E3A5F;
            letter-spacing: -0.02em; margin: 0.25rem 0;
        }
        .hero-result .margin {
            font-size: 0.85rem; color: #7A8FA6; margin-top: 0.5rem;
        }
        .hero-result .margin span {
            background: #1E3A5F; color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 6px; font-weight: 500;
        }

        /* ── Pipeline steps ── */
        .step-row {
            display: flex; align-items: flex-start; gap: 0.75rem;
            padding: 0.85rem 0; border-bottom: 1px solid #E8ECF1;
        }
        .step-row:last-child { border-bottom: none; }
        .step-badge {
            background: linear-gradient(135deg, #1E3A5F, #2C5282);
            color: white;
            width: 28px; height: 28px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.72rem; font-weight: 700; flex-shrink: 0;
            box-shadow: 0 2px 6px rgba(30,58,95,0.2);
        }
        .step-content {
            font-size: 0.88rem; color: #4A5568; line-height: 1.5;
        }
        .step-content strong { color: #1E3A5F; }

        /* ── Dividers ── */
        hr { border-color: #E8ECF1 !important; }

        /* ── Buttons ── */
        .stButton > button {
            background: linear-gradient(135deg, #1E3A5F, #2C5282);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #D4872E, #F0A04B);
            box-shadow: 0 4px 12px rgba(212,135,46,0.3);
        }

        /* ── Download button ── */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #D4872E, #F0A04B);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
        }
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #1E3A5F, #2C5282);
        }

        /* ── Slider accent ── */
        .stSlider [data-testid="stThumbValue"] {
            color: #D4872E;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)
