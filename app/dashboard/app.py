"""
California Housing — Dashboard SaaS
Sidebar filters | Header metrics | 5 Tabs
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.core.model_loader import predict, load_artifacts


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GEOCODING (cached)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@st.cache_data(ttl=3600, show_spinner=False)
def geocode_address(address: str):
    """Geocode an address — cached 1h to avoid repeat API calls."""
    geolocator = Nominatim(user_agent="california_housing_dashboard")
    query = address if "CA" in address.upper() or "CALIFORNIA" in address.upper() else f"{address}, California, USA"
    try:
        location = geolocator.geocode(query, timeout=10)
        if location and 32.0 <= location.latitude <= 42.0 and -125.0 <= location.longitude <= -114.0:
            return {"lat": round(location.latitude, 4), "lon": round(location.longitude, 4), "addr": location.address}
        elif location:
            return {"error": "not_california"}
        return {"error": "not_found"}
    except (GeocoderTimedOut, GeocoderUnavailable):
        return {"error": "timeout"}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="California Housing",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS — SaaS Dashboard Theme
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }

    /* ── Metric cards ── */
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
        font-size: 0.78rem;
        font-weight: 500;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: #111827;
    }

    /* ── Plotly containers ── */
    [data-testid="stPlotlyChart"] > div {
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        overflow: hidden;
        background: #FFFFFF;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #F9FAFB;
        border-radius: 10px;
        padding: 4px;
        border: 1px solid #E5E7EB;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        font-size: 0.88rem;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }

    /* ── Custom classes ── */
    .sidebar-header {
        padding: 1.25rem 0.75rem 0.75rem;
    }
    .sidebar-header h2 {
        font-size: 1.15rem;
        font-weight: 700;
        color: #111827;
        margin: 0 0 2px 0;
    }
    .sidebar-header p {
        font-size: 0.78rem;
        color: #9CA3AF;
        margin: 0;
    }
    .sidebar-section {
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #9CA3AF;
        padding: 1rem 0.75rem 0.25rem;
    }
    .sidebar-footer {
        padding: 0.75rem;
        margin-top: 1rem;
        border-top: 1px solid #F3F4F6;
        font-size: 0.72rem;
        color: #D1D5DB;
        line-height: 1.6;
    }

    .section-label {
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #9CA3AF;
        margin-bottom: 0.5rem;
    }

    hr { border-color: #F3F4F6 !important; }

    /* ── Hero result card ── */
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
        font-size: 0.85rem;
        font-weight: 500;
        color: #6B7280;
        margin-bottom: 0.25rem;
    }
    .hero-result .price {
        font-size: 3.25rem;
        font-weight: 800;
        color: #111827;
        letter-spacing: -0.02em;
        margin: 0.25rem 0;
    }
    .hero-result .margin {
        font-size: 0.85rem;
        color: #6B7280;
        margin-top: 0.5rem;
    }
    .hero-result .margin span {
        background: #F3F4F6;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: 500;
    }

    /* ── Pipeline steps ── */
    .step-row {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.85rem 0;
        border-bottom: 1px solid #F3F4F6;
    }
    .step-row:last-child { border-bottom: none; }
    .step-badge {
        background: #4F46E5;
        color: white;
        width: 26px; height: 26px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.72rem; font-weight: 700; flex-shrink: 0;
    }
    .step-content {
        font-size: 0.88rem;
        color: #4B5563;
        line-height: 1.5;
    }
    .step-content strong { color: #111827; }

    /* ── Info box ── */
    .info-box {
        background: #F0F9FF;
        border: 1px solid #BAE6FD;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        font-size: 0.85rem;
        color: #0C4A6E;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA
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

df_raw = load_data()
test_preds = load_test_predictions()
artifacts = load_artifacts()
metrics = artifacts["metrics"]

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

# Plotly shared layout
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
    "primary": "#4F46E5",     # indigo
    "secondary": "#0EA5E9",   # sky
    "success": "#10B981",     # emerald
    "danger": "#EF4444",      # red
    "warning": "#F59E0B",     # amber
    "muted": "#9CA3AF",       # gray
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR — Filtres globaux + description
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2>California Housing</h2>
        <p>Analyse et prediction immobiliere</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Filtres globaux</div>', unsafe_allow_html=True)

    price_range = st.slider(
        "Tranche de prix (x$100k)",
        float(df_raw["MedHouseVal"].min()),
        float(df_raw["MedHouseVal"].max()),
        (0.15, 5.0),
        step=0.05,
    )

    income_range = st.slider(
        "Revenu median (x$10k)",
        float(df_raw["MedInc"].min()),
        float(df_raw["MedInc"].max()),
        (0.5, 15.0),
        step=0.1,
    )

    # Apply filters
    df = df_raw[
        (df_raw["MedHouseVal"] >= price_range[0]) &
        (df_raw["MedHouseVal"] <= price_range[1]) &
        (df_raw["MedInc"] >= income_range[0]) &
        (df_raw["MedInc"] <= income_range[1])
    ].copy()

    st.markdown("---")
    st.markdown(f"""
    <div class="sidebar-footer">
        <strong>{len(df):,}</strong> districts affiches / {len(df_raw):,}<br>
        Source : Recensement US 1990<br>
        Modele : Regression lineaire + K-Means
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEADER — Metric cards
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
h1, h2, h3, h4 = st.columns(4)
h1.metric("Prix moyen", f"${df['MedHouseVal'].mean() * 100_000:,.0f}")
h2.metric("Revenu median", f"${df['MedInc'].mean() * 10_000:,.0f}")
h3.metric("Districts analyses", f"{len(df):,}")
h4.metric("Precision du modele", f"{metrics['r2']*100:.0f}%")

st.markdown("")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TABS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tab_explore, tab_model, tab_predict, tab_compare, tab_about = st.tabs([
    "Analyse exploratoire",
    "Performance du modele",
    "Predire un prix",
    "Comparer deux districts",
    "A propos",
])


# ──────────────────────────────────────────────────────────
# TAB 1 : ANALYSE EXPLORATOIRE
# ──────────────────────────────────────────────────────────
with tab_explore:
    st.markdown("")

    # ── Carte ──
    st.markdown('<div class="section-label">Carte geographique</div>', unsafe_allow_html=True)

    map_col1, map_col2 = st.columns([4, 1])

    with map_col2:
        map_color = st.selectbox(
            "Colorer par",
            ["MedHouseVal", "MedInc", "HouseAge", "Population"],
            format_func=lambda x: LABELS.get(x, x),
            key="map_color",
        )
        map_n = st.slider("Points affiches", 2000, min(len(df), 15000), min(6000, len(df)), 500, key="map_n")

    df_map = df.sample(n=min(map_n, len(df)), random_state=42)

    cscale = "Purples" if map_color == "MedHouseVal" else "Blues" if map_color == "MedInc" else "YlOrRd"

    fig_map = px.scatter_map(
        df_map,
        lat="Latitude", lon="Longitude",
        color=map_color,
        size=np.clip(df_map["Population"], 80, 4000),
        size_max=9,
        color_continuous_scale=cscale,
        map_style="carto-positron",
        zoom=4.8,
        center={"lat": 36.7, "lon": -119.5},
        height=520,
        hover_data={
            "MedHouseVal": ":.2f", "MedInc": ":.2f",
            "HouseAge": ":.0f", "Population": ":,.0f",
            "Latitude": False, "Longitude": False,
        },
        labels=LABELS,
    )
    fig_map.update_layout(
        **{k: v for k, v in PL.items() if k != "margin"},
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title=dict(text=LABELS.get(map_color, map_color), font=dict(size=11)),
            thickness=14, len=0.45, yanchor="middle", y=0.5,
        ),
    )
    with map_col1:
        st.plotly_chart(fig_map, width="stretch")

    st.markdown("")
    st.markdown("---")

    # ── Correlations ──
    st.markdown('<div class="section-label">Correlations</div>', unsafe_allow_html=True)

    corr = df.corr(numeric_only=True).round(3)
    corr_labels = corr.rename(index=LABELS, columns=LABELS)

    fig_corr = px.imshow(
        corr_labels,
        text_auto=".2f",
        color_continuous_scale=["#EF4444", "#FAFAFA", "#10B981"],
        zmin=-1, zmax=1,
        aspect="auto",
    )
    fig_corr.update_layout(
        **PL,
        height=500,
        title="",
        coloraxis_colorbar=dict(title="r", thickness=12),
    )
    fig_corr.update_traces(textfont=dict(size=11))
    st.plotly_chart(fig_corr, width="stretch")

    st.markdown("""
    <div class="info-box">
        Le <strong>revenu median</strong> est le meilleur predicteur du prix (r = 0.69).
        La <strong>latitude</strong> et la <strong>longitude</strong> capturent l'effet geographique.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("---")

    # ── Distribution ──
    st.markdown('<div class="section-label">Distribution</div>', unsafe_allow_html=True)

    dist_col1, dist_col2 = st.columns([3, 1])
    with dist_col2:
        dist_var = st.selectbox(
            "Variable",
            df.columns.tolist(),
            format_func=lambda x: LABELS.get(x, x),
            key="dist_var",
        )

    fig_dist = px.histogram(
        df, x=dist_var, nbins=60,
        color_discrete_sequence=[C["primary"]],
    )
    fig_dist.update_layout(
        **PL,
        title=LABELS.get(dist_var, dist_var),
        xaxis_title="",
        yaxis_title="Districts",
        bargap=0.02,
        height=380,
    )
    with dist_col1:
        st.plotly_chart(fig_dist, width="stretch")

    with st.expander("Voir les statistiques detaillees"):
        st.dataframe(
            df.describe().round(2).rename(columns=LABELS),
            width="stretch",
        )


# ──────────────────────────────────────────────────────────
# TAB 2 : PERFORMANCE DU MODELE
# ──────────────────────────────────────────────────────────
with tab_model:
    st.markdown("")

    # ── Metrics row ──
    pm1, pm2, pm3, pm4 = st.columns(4)
    pm1.metric("R²", f"{metrics['r2']:.4f}", help="Part de variance expliquee par le modele")
    pm2.metric("MAE", f"${metrics['mae']*100_000:,.0f}", help="Erreur absolue moyenne en dollars")
    pm3.metric("RMSE", f"{metrics['rmse']:.4f}", help="Racine de l'erreur quadratique moyenne")
    pm4.metric("Clusters geographiques", "1 000", help="K-Means sur Latitude/Longitude")

    st.markdown("")

    if test_preds is not None:
        pred_col1, pred_col2 = st.columns(2)

        # ── Actual vs Predicted ──
        with pred_col1:
            st.markdown('<div class="section-label">Reel vs Predit</div>', unsafe_allow_html=True)

            fig_avp = go.Figure()
            fig_avp.add_trace(go.Scatter(
                x=test_preds["actual"],
                y=test_preds["predicted"],
                mode="markers",
                marker=dict(size=3, color=C["primary"], opacity=0.2),
                name="Predictions",
            ))
            # Perfect line
            line_min = min(test_preds["actual"].min(), test_preds["predicted"].min())
            line_max = max(test_preds["actual"].max(), test_preds["predicted"].max())
            fig_avp.add_trace(go.Scatter(
                x=[line_min, line_max], y=[line_min, line_max],
                mode="lines",
                line=dict(color=C["danger"], width=1.5, dash="dash"),
                name="Prediction parfaite",
            ))
            fig_avp.update_layout(
                **PL,
                title="Valeurs reelles vs predites",
                xaxis_title="Prix reel (x$100k)",
                yaxis_title="Prix predit (x$100k)",
                height=420,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            )
            st.plotly_chart(fig_avp, width="stretch")

        # ── Residuals ──
        with pred_col2:
            st.markdown('<div class="section-label">Distribution des residus</div>', unsafe_allow_html=True)

            fig_res = px.histogram(
                test_preds, x="residual", nbins=60,
                color_discrete_sequence=[C["success"]],
            )
            fig_res.add_vline(
                x=0, line_dash="dash", line_color=C["danger"], line_width=1.5,
            )
            fig_res.update_layout(
                **PL,
                title="Residus (reel - predit)",
                xaxis_title="Erreur (x$100k)",
                yaxis_title="Frequence",
                height=420,
                bargap=0.02,
            )
            st.plotly_chart(fig_res, width="stretch")

        st.markdown("")

        # ── Residuals scatter ──
        st.markdown('<div class="section-label">Residus vs valeurs predites</div>', unsafe_allow_html=True)

        fig_res_sc = go.Figure()
        fig_res_sc.add_trace(go.Scatter(
            x=test_preds["predicted"],
            y=test_preds["residual"],
            mode="markers",
            marker=dict(size=3, color=C["secondary"], opacity=0.2),
        ))
        fig_res_sc.add_hline(y=0, line_dash="dash", line_color=C["danger"], line_width=1.5)
        fig_res_sc.update_layout(
            **PL,
            title="Analyse des residus",
            xaxis_title="Prix predit (x$100k)",
            yaxis_title="Residu",
            height=380,
            showlegend=False,
        )
        st.plotly_chart(fig_res_sc, width="stretch")

    st.markdown("---")

    # ── Coefficients ──
    st.markdown('<div class="section-label">Importance des variables</div>', unsafe_allow_html=True)

    model = artifacts["model"]
    base_names = artifacts["feature_names_base"]
    base_coefs = model.coef_[:len(base_names)]

    coef_df = pd.DataFrame({
        "Feature": [LABELS.get(n, n) for n in base_names],
        "Coefficient": base_coefs,
        "Impact": ["Positif" if c > 0 else "Negatif" for c in base_coefs],
    }).sort_values("Coefficient", key=abs, ascending=True)

    fig_coef = px.bar(
        coef_df, x="Coefficient", y="Feature",
        orientation="h",
        color="Impact",
        color_discrete_map={"Positif": C["primary"], "Negatif": C["danger"]},
    )
    fig_coef.update_layout(
        **PL,
        height=360,
        title="Coefficients standardises (features de base)",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_coef, width="stretch")

    st.markdown("---")

    # ── Pipeline ──
    st.markdown('<div class="section-label">Pipeline de prediction</div>', unsafe_allow_html=True)

    steps = [
        ("Nettoyage", "Retrait des outliers (IQR x 3) sur AveRooms, AveBedrms, AveOccup, Population"),
        ("Feature engineering", "Creation de 2 nouvelles variables : BedroomRatio et IncomeLocation"),
        ("Clustering", "K-Means (K=1000) sur les coordonnees geographiques, encode en one-hot"),
        ("Standardisation", "StandardScaler ajuste uniquement sur le jeu d'entrainement"),
        ("Prediction", "Regression lineaire multiple sur 1 010 features au total"),
    ]

    for i, (title, desc) in enumerate(steps, 1):
        st.markdown(f"""
        <div class="step-row">
            <div class="step-badge">{i}</div>
            <div class="step-content"><strong>{title}</strong> — {desc}</div>
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
# TAB 3 : PREDIRE UN PRIX
# ──────────────────────────────────────────────────────────
with tab_predict:
    st.markdown("")

    st.markdown("""
    <div class="info-box">
        Ajustez les caracteristiques d'un district californien pour obtenir une estimation
        du prix median des logements. Le modele utilise 1 010 features incluant le clustering
        geographique.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # ── Form ──
    form_left, form_spacer, form_right = st.columns([5, 0.5, 5])

    with form_left:
        st.markdown('<div class="section-label">Economie & population</div>', unsafe_allow_html=True)
        med_inc = st.number_input(
            "Revenu median du quartier (x$10k)",
            min_value=0.5, max_value=15.0, value=3.87, step=0.1,
            format="%.2f",
            help="Revenu median des menages en dizaines de milliers de dollars",
        )
        population = st.number_input("Population du district", min_value=3, max_value=35000, value=1425, step=50)
        ave_occup = st.number_input("Occupants par logement (moyenne)", min_value=0.5, max_value=10.0, value=3.07, step=0.1, format="%.2f")

    with form_right:
        st.markdown('<div class="section-label">Caracteristiques du logement</div>', unsafe_allow_html=True)
        house_age = st.number_input("Age median des logements (annees)", min_value=1, max_value=52, value=29, step=1)
        ave_rooms = st.number_input("Nombre de pieces (moyenne)", min_value=1.0, max_value=15.0, value=5.43, step=0.1, format="%.2f")
        ave_bedrms = st.number_input("Nombre de chambres (moyenne)", min_value=0.3, max_value=5.0, value=1.10, step=0.1, format="%.2f")

    st.markdown("---")
    st.markdown('<div class="section-label">Localisation du district</div>', unsafe_allow_html=True)

    address = st.text_input(
        "Adresse en Californie",
        placeholder="Ex: 123 Market Street, San Francisco, CA",
        help="Tapez une adresse et appuyez sur Entree pour localiser automatiquement.",
        key="predict_address",
    )

    # Default coordinates
    latitude = 35.63
    longitude = -119.57

    if address:
        result = geocode_address(address)
        if "error" not in result:
            latitude = result["lat"]
            longitude = result["lon"]
            st.markdown(f"""
            <div style="background:#F0F0FF; border:1px solid #E0E0F0; border-radius:10px; padding:0.75rem 1rem; margin:0.5rem 0; font-size:0.85rem; color:#4F46E5;">
                <strong>Adresse resolue :</strong> {result['addr']}<br>
                <strong>Coordonnees :</strong> {latitude}, {longitude}
            </div>
            """, unsafe_allow_html=True)
        elif result["error"] == "not_california":
            st.warning("Cette adresse ne semble pas etre en Californie.")
        elif result["error"] == "timeout":
            st.error("Service de geocodage temporairement indisponible. Reessayez.")
        else:
            st.warning("Adresse introuvable. Verifiez l'orthographe.")

    # Scatter mapbox with nearby districts
    df_nearby = df_raw[
        (df_raw["Latitude"].between(latitude - 0.3, latitude + 0.3)) &
        (df_raw["Longitude"].between(longitude - 0.3, longitude + 0.3))
    ].copy()

    fig_pred_map = px.scatter_map(
        df_nearby if len(df_nearby) > 0 else df_raw.sample(500, random_state=42),
        lat="Latitude", lon="Longitude",
        color="MedHouseVal",
        size_max=8,
        color_continuous_scale="Purples",
        map_style="carto-positron",
        zoom=10 if address and len(df_nearby) > 0 else 5,
        center={"lat": latitude, "lon": longitude},
        height=400,
        labels=LABELS,
        hover_data={"MedHouseVal": ":.2f", "MedInc": ":.2f", "Latitude": False, "Longitude": False},
    )
    # Add marker for selected location
    fig_pred_map.add_trace(go.Scattermap(
        lat=[latitude], lon=[longitude],
        mode="markers+text",
        marker=dict(size=16, color="#EF4444", symbol="circle"),
        text=["Votre district"],
        textposition="top center",
        textfont=dict(size=12, color="#EF4444", family="Inter"),
        name="Votre district",
        showlegend=False,
    ))
    fig_pred_map.update_layout(
        **{k: v for k, v in PL.items() if k != "margin"},
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(title=dict(text="Prix", font=dict(size=11)), thickness=12, len=0.4),
    )
    st.plotly_chart(fig_pred_map, width="stretch")

    # Fallback: manual override
    with st.expander("Ajuster manuellement les coordonnees"):
        manual_col1, manual_col2 = st.columns(2)
        with manual_col1:
            latitude = st.number_input("Latitude", min_value=32.0, max_value=42.0, value=latitude, step=0.01, format="%.4f", key="pred_lat")
        with manual_col2:
            longitude = st.number_input("Longitude", min_value=-125.0, max_value=-114.0, value=longitude, step=0.01, format="%.4f", key="pred_lon")

    st.markdown("")

    # ── Predict ──
    if st.button("Estimer le prix", type="primary", width="stretch"):

        input_data = {
            "MedInc": med_inc,
            "HouseAge": float(house_age),
            "AveRooms": ave_rooms,
            "AveBedrms": ave_bedrms,
            "Population": float(population),
            "AveOccup": ave_occup,
            "Latitude": latitude,
            "Longitude": longitude,
        }

        with st.spinner("Calcul en cours..."):
            price = predict(input_data)
            price_dollars = price * 100_000
            mae_dollars = metrics["mae"] * 100_000

        # Hero result
        st.markdown(f"""
        <div class="hero-result">
            <div class="label">Prix median estime</div>
            <div class="price">${price_dollars:,.0f}</div>
            <div class="margin">Marge d'erreur : <span>+/- ${mae_dollars:,.0f}</span></div>
        </div>
        """, unsafe_allow_html=True)

        # Detail row
        r1, r2, r3 = st.columns(3)
        r1.metric("Valeur brute", f"{price:.3f} x$100k")
        r2.metric("Erreur moyenne (MAE)", f"${mae_dollars:,.0f}")
        r3.metric("Fiabilite du modele", f"{metrics['r2']*100:.0f}%")

        # Distribution with prediction line
        st.markdown("")
        st.markdown('<div class="section-label">Position dans la distribution</div>', unsafe_allow_html=True)

        fig_pos = px.histogram(
            df_raw, x="MedHouseVal", nbins=80,
            color_discrete_sequence=["#E0E7FF"],
            labels={"MedHouseVal": "Prix median (x$100k)"},
        )
        fig_pos.add_vline(
            x=price, line_dash="solid", line_color=C["primary"], line_width=3,
            annotation_text=f"Votre estimation : ${price_dollars:,.0f}",
            annotation_position="top",
            annotation_font=dict(size=12, color=C["primary"], family="Inter"),
        )
        percentile = (df_raw["MedHouseVal"] < price).mean() * 100
        fig_pos.update_layout(
            **PL,
            height=320,
            title=f"Votre estimation se situe au {percentile:.0f}e percentile",
            xaxis_title="Prix median (x$100k)",
            yaxis_title="Nombre de districts",
            bargap=0.02,
        )
        st.plotly_chart(fig_pos, width="stretch")


# ──────────────────────────────────────────────────────────
# TAB 4 : COMPARER DEUX DISTRICTS
# ──────────────────────────────────────────────────────────
with tab_compare:
    st.markdown("")

    st.markdown("""
    <div class="info-box">
        Comparez deux adresses en Californie : le modele estimera le prix pour chaque
        district et vous pourrez visualiser les differences.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    comp1, comp_spacer, comp2 = st.columns([5, 0.5, 5])

    # ── District A ──
    with comp1:
        st.markdown('<div class="section-label">District A</div>', unsafe_allow_html=True)
        addr_a = st.text_input("Adresse", placeholder="Ex: Venice Beach, Los Angeles", key="addr_a")
        a_inc = st.number_input("Revenu median (x$10k)", 0.5, 15.0, 4.5, 0.1, format="%.2f", key="a_inc")
        a_age = st.number_input("Age median logements", 1, 52, 25, 1, key="a_age")
        a_rooms = st.number_input("Pieces (moy.)", 1.0, 15.0, 5.5, 0.1, format="%.2f", key="a_rooms")
        a_bedrms = st.number_input("Chambres (moy.)", 0.3, 5.0, 1.1, 0.1, format="%.2f", key="a_bedrms")
        a_pop = st.number_input("Population", 3, 35000, 1500, 50, key="a_pop")
        a_occup = st.number_input("Occupants (moy.)", 0.5, 10.0, 3.0, 0.1, format="%.2f", key="a_occup")

    # ── District B ──
    with comp2:
        st.markdown('<div class="section-label">District B</div>', unsafe_allow_html=True)
        addr_b = st.text_input("Adresse", placeholder="Ex: Palo Alto, CA", key="addr_b")
        b_inc = st.number_input("Revenu median (x$10k)", 0.5, 15.0, 8.0, 0.1, format="%.2f", key="b_inc")
        b_age = st.number_input("Age median logements", 1, 52, 35, 1, key="b_age")
        b_rooms = st.number_input("Pieces (moy.)", 1.0, 15.0, 6.5, 0.1, format="%.2f", key="b_rooms")
        b_bedrms = st.number_input("Chambres (moy.)", 0.3, 5.0, 1.0, 0.1, format="%.2f", key="b_bedrms")
        b_pop = st.number_input("Population", 3, 35000, 2000, 50, key="b_pop")
        b_occup = st.number_input("Occupants (moy.)", 0.5, 10.0, 2.8, 0.1, format="%.2f", key="b_occup")

    # Geocode both
    lat_a, lon_a, label_a = 34.0, -118.5, "District A"
    lat_b, lon_b, label_b = 37.4, -122.1, "District B"

    if addr_a:
        res_a = geocode_address(addr_a)
        if "error" not in res_a:
            lat_a, lon_a = res_a["lat"], res_a["lon"]
            label_a = res_a["addr"].split(",")[0]

    if addr_b:
        res_b = geocode_address(addr_b)
        if "error" not in res_b:
            lat_b, lon_b = res_b["lat"], res_b["lon"]
            label_b = res_b["addr"].split(",")[0]

    st.markdown("---")

    if st.button("Comparer", type="primary", width="stretch"):
        data_a = {"MedInc": a_inc, "HouseAge": float(a_age), "AveRooms": a_rooms, "AveBedrms": a_bedrms,
                   "Population": float(a_pop), "AveOccup": a_occup, "Latitude": lat_a, "Longitude": lon_a}
        data_b = {"MedInc": b_inc, "HouseAge": float(b_age), "AveRooms": b_rooms, "AveBedrms": b_bedrms,
                   "Population": float(b_pop), "AveOccup": b_occup, "Latitude": lat_b, "Longitude": lon_b}

        with st.spinner("Calcul en cours..."):
            price_a = predict(data_a) * 100_000
            price_b = predict(data_b) * 100_000
            diff = price_b - price_a
            diff_pct = (diff / price_a * 100) if price_a > 0 else 0

        # Results side by side
        res1, res_sp, res2 = st.columns([5, 0.5, 5])
        with res1:
            st.markdown(f"""
            <div class="hero-result" style="background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%); border-color: #A5B4FC;">
                <div class="label">{label_a}</div>
                <div class="price" style="font-size:2.5rem;">${price_a:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        with res2:
            st.markdown(f"""
            <div class="hero-result" style="background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%); border-color: #86EFAC;">
                <div class="label">{label_b}</div>
                <div class="price" style="font-size:2.5rem;">${price_b:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        # Difference
        color_diff = C["success"] if diff > 0 else C["danger"]
        sign = "+" if diff > 0 else ""
        st.markdown(f"""
        <div style="text-align:center; padding:1rem; margin:0.5rem 0;">
            <span style="font-size:1.5rem; font-weight:700; color:{color_diff};">
                {sign}${diff:,.0f} ({sign}{diff_pct:.1f}%)
            </span>
            <br><span style="font-size:0.85rem; color:#6B7280;">Difference B vs A</span>
        </div>
        """, unsafe_allow_html=True)

        # Map with both points
        fig_comp_map = px.scatter_map(
            df_raw.sample(min(3000, len(df_raw)), random_state=42),
            lat="Latitude", lon="Longitude",
            color="MedHouseVal",
            size_max=6,
            color_continuous_scale="Purples",
            map_style="carto-positron",
            zoom=5,
            center={"lat": (lat_a + lat_b) / 2, "lon": (lon_a + lon_b) / 2},
            height=420,
            labels=LABELS,
            opacity=0.3,
        )
        fig_comp_map.add_trace(go.Scattermap(
            lat=[lat_a, lat_b], lon=[lon_a, lon_b],
            mode="markers+text",
            marker=dict(size=[18, 18], color=[C["primary"], C["success"]]),
            text=[f"A: ${price_a:,.0f}", f"B: ${price_b:,.0f}"],
            textposition="top center",
            textfont=dict(size=13, family="Inter"),
            name="Districts compares",
        ))
        fig_comp_map.update_layout(
            **{k: v for k, v in PL.items() if k != "margin"},
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            coloraxis_colorbar=dict(title=dict(text="Prix", font=dict(size=11)), thickness=12, len=0.35),
        )
        st.plotly_chart(fig_comp_map, width="stretch")

        # Comparison table
        st.markdown('<div class="section-label">Detail de la comparaison</div>', unsafe_allow_html=True)
        comp_df = pd.DataFrame({
            "Caracteristique": ["Revenu median (x$10k)", "Age logements", "Pieces (moy.)", "Chambres (moy.)", "Population", "Occupants (moy.)", "Prix estime"],
            label_a: [a_inc, a_age, a_rooms, a_bedrms, a_pop, a_occup, f"${price_a:,.0f}"],
            label_b: [b_inc, b_age, b_rooms, b_bedrms, b_pop, b_occup, f"${price_b:,.0f}"],
        })
        st.dataframe(comp_df, width="stretch", hide_index=True)


# ──────────────────────────────────────────────────────────
# TAB 5 : A PROPOS
# ──────────────────────────────────────────────────────────
with tab_about:
    st.markdown("")

    st.markdown("""
    <div class="section-label">Le projet</div>

    Ce dashboard presente une analyse du marche immobilier californien basee sur les donnees
    du **recensement americain de 1990**. L'objectif est d'estimer le prix median des logements
    d'un district a partir de ses caracteristiques socio-economiques et geographiques.

    ---

    <div class="section-label">Donnees</div>

    Le dataset **California Housing** contient **20 640 districts** decrits par 8 variables :
    revenu median, age des logements, nombre de pieces et chambres (moyennes), population,
    nombre d'occupants, latitude et longitude. La variable cible est le prix median des logements
    en centaines de milliers de dollars.

    **Limites importantes :**
    - Les prix sont **plafonnes a $500 000** (valeurs censurees a 5.0) — le modele ne peut pas
      predire au-dela de ce seuil
    - Les donnees datent de **1990** — elles ne refletent pas le marche actuel
    - Les variables sont des **moyennes par district**, pas des valeurs individuelles

    ---

    <div class="section-label">Modele</div>
    """, unsafe_allow_html=True)

    about1, about2 = st.columns(2)
    with about1:
        st.markdown("""
        **Pipeline d'entrainement :**
        1. Nettoyage des outliers (IQR x 3)
        2. Feature engineering : BedroomRatio, IncomeLocation
        3. Clustering geographique (K-Means, K=1000)
        4. One-hot encoding des clusters
        5. StandardScaler (ajuste sur le train uniquement)
        6. Regression lineaire multiple (1 010 features)
        """)
    with about2:
        st.markdown(f"""
        **Performances sur le jeu de test :**
        - **R²** = {metrics['r2']:.4f} ({metrics['r2']*100:.1f}% de variance expliquee)
        - **MAE** = ${metrics['mae']*100_000:,.0f} (erreur moyenne)
        - **RMSE** = {metrics['rmse']:.4f}

        **Pourquoi la regression lineaire ?**
        C'est un choix pedagogique : le modele reste interpretable
        (coefficients lisibles) tout en atteignant un R² > 0.82
        grace au feature engineering et au clustering.
        """)

    st.markdown("""
    ---

    <div class="section-label">Technologies</div>

    - **Backend** : FastAPI (API REST pour les predictions)
    - **Dashboard** : Streamlit + Plotly (visualisations interactives)
    - **ML** : scikit-learn (regression, clustering, preprocessing)
    - **Geocodage** : geopy + Nominatim (OpenStreetMap, gratuit)
    - **Deploiement** : Streamlit Cloud

    ---

    <div class="section-label">Auteur</div>

    Projet realise par **Mathis Ruiz** dans le cadre d'un projet de Machine Learning.

    [Code source sur GitHub](https://github.com/reumps/California_House)
    """, unsafe_allow_html=True)
