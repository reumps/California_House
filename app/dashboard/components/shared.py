"""Shared components: CSS, data loading, constants."""

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
# LABELS & COLORS
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

PL = dict(
    font=dict(family="Inter, -apple-system, sans-serif", color="#374151", size=12),
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=48, r=24, t=48, b=40),
    title_font=dict(size=14, color="#374151", family="Inter, sans-serif"),
    xaxis=dict(gridcolor="#F3F4F6", zeroline=False, linecolor="#E5E7EB"),
    yaxis=dict(gridcolor="#F3F4F6", zeroline=False, linecolor="#E5E7EB"),
)

C = {
    "primary": "#4F46E5",
    "secondary": "#0EA5E9",
    "success": "#10B981",
    "danger": "#EF4444",
    "warning": "#F59E0B",
    "muted": "#9CA3AF",
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        #MainMenu, footer, header { visibility: hidden; }

        [data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid #E5E7EB;
        }

        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
            transition: box-shadow 0.2s ease;
        }
        [data-testid="stMetric"]:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.78rem; font-weight: 500; color: #6B7280;
            text-transform: uppercase; letter-spacing: 0.04em;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.75rem; font-weight: 700; color: #111827;
        }

        [data-testid="stPlotlyChart"] > div {
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            overflow: hidden;
            background: #FFFFFF;
        }

        [data-testid="stExpander"] {
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }

        .section-label {
            font-size: 0.68rem; font-weight: 600;
            text-transform: uppercase; letter-spacing: 0.07em;
            color: #9CA3AF; margin-bottom: 0.5rem;
        }

        .info-box {
            background: #F0F9FF;
            border: 1px solid #BAE6FD;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            font-size: 0.85rem;
            color: #0C4A6E;
            margin: 1rem 0;
        }

        .hero-result {
            text-align: center;
            padding: 2.5rem 2rem;
            background: linear-gradient(135deg, #EEF2FF 0%, #F0FDF4 50%, #FFF7ED 100%);
            border: 1px solid #C7D2FE;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(99,102,241,0.08);
            margin: 1rem 0 1.5rem;
        }
        .hero-result .label {
            font-size: 0.85rem; font-weight: 500; color: #6B7280; margin-bottom: 0.25rem;
        }
        .hero-result .price {
            font-size: 3.25rem; font-weight: 800; color: #111827;
            letter-spacing: -0.02em; margin: 0.25rem 0;
        }
        .hero-result .margin {
            font-size: 0.85rem; color: #6B7280; margin-top: 0.5rem;
        }
        .hero-result .margin span {
            background: #F3F4F6; padding: 0.2rem 0.6rem;
            border-radius: 6px; font-weight: 500;
        }

        .step-row {
            display: flex; align-items: flex-start; gap: 0.75rem;
            padding: 0.85rem 0; border-bottom: 1px solid #F3F4F6;
        }
        .step-row:last-child { border-bottom: none; }
        .step-badge {
            background: #4F46E5; color: white;
            width: 26px; height: 26px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.72rem; font-weight: 700; flex-shrink: 0;
        }
        .step-content {
            font-size: 0.88rem; color: #4B5563; line-height: 1.5;
        }
        .step-content strong { color: #111827; }

        hr { border-color: #F3F4F6 !important; }
    </style>
    """, unsafe_allow_html=True)
