"""
CaliPredict — California Housing Analytics & AI Predictions
Single-page app with top navigation tabs (no sidebar).
"""

import streamlit as st
import pandas as pd
from components.shared import inject_css, show_logo, load_data, load_artifacts, LABELS, COLUMN_DESCRIPTIONS

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="CaliPredict",
    page_icon="C",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_css()
show_logo()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOP NAVIGATION — tabs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tab_accueil, tab_explo, tab_analyse, tab_pred = st.tabs([
    "Accueil",
    "Exploration des donnees",
    "Analyse approfondie",
    "Prediction interactive",
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 : ACCUEIL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_accueil:
    df = load_data()
    artifacts = load_artifacts()
    metrics = artifacts["metrics"]

    st.markdown("# CaliPredict")
    st.markdown("### California Housing Analytics & AI Predictions")
    st.markdown("")

    st.markdown("""
    Ce projet analyse le marche immobilier californien a partir des donnees du **recensement americain de 1990**.
    Le dataset **California Housing** regroupe les informations de **20 640 districts** decrits par 8 variables
    socio-economiques et geographiques. L'objectif est de comprendre quels facteurs influencent le prix median
    des logements et de construire un modele predictif fiable.

    La question centrale est : **quels sont les determinants principaux du prix immobilier en Californie,
    et peut-on predire le prix median d'un district a partir de ses caracteristiques ?**
    Pour y repondre, nous combinons une analyse exploratoire approfondie avec un modele de regression lineaire
    enrichi par du clustering geographique (K-Means, K=1000), atteignant un R2 de {r2:.1f}%.

    Les donnees presentent certaines limites importantes : les prix sont **plafonnes a $500 000**, les donnees
    datent de **1990** et ne refletent pas le marche actuel, et les variables representent des **moyennes par
    district** et non des valeurs individuelles. Malgre ces limites, le dataset reste une reference
    pedagogique pour l'apprentissage du machine learning applique a l'immobilier.
    """.format(r2=metrics['r2'] * 100))

    st.markdown("---")

    # 4 KPIs
    st.markdown('<div class="section-label">Metriques cles</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Nombre de lignes", f"{len(df):,}")
    k2.metric("Nombre de colonnes", f"{len(df.columns)}")
    k3.metric("Valeurs manquantes", f"{df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100:.1f}%")

    above_cap = (df["MedHouseVal"] >= 5.0).mean() * 100
    k4.metric("Prix plafonnes (>=500k$)", f"{above_cap:.1f}%")

    st.markdown("")
    st.markdown("---")

    # Apercu des donnees
    st.markdown('<div class="section-label">Apercu des donnees</div>', unsafe_allow_html=True)

    st.dataframe(
        df.head(100).rename(columns=LABELS),
        width="stretch",
        hide_index=True,
        height=400,
    )

    st.markdown("")
    st.markdown("---")

    # Description des colonnes
    st.markdown('<div class="section-label">Description des colonnes</div>', unsafe_allow_html=True)

    col_df = pd.DataFrame({
        "Variable": list(COLUMN_DESCRIPTIONS.keys()),
        "Description": list(COLUMN_DESCRIPTIONS.values()),
        "Type": [str(df[col].dtype) for col in COLUMN_DESCRIPTIONS.keys()],
        "Min": [f"{df[col].min():.2f}" for col in COLUMN_DESCRIPTIONS.keys()],
        "Max": [f"{df[col].max():.2f}" for col in COLUMN_DESCRIPTIONS.keys()],
        "Moyenne": [f"{df[col].mean():.2f}" for col in COLUMN_DESCRIPTIONS.keys()],
    })

    st.dataframe(col_df, width="stretch", hide_index=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 : EXPLORATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_explo:
    from pages.exploration import render as render_exploration
    render_exploration()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 : ANALYSE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_analyse:
    from pages.analyse import render as render_analyse
    render_analyse()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4 : PREDICTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_pred:
    from pages.prediction import render as render_prediction
    render_prediction()
