"""
California Housing — Page 3 : Analyse Approfondie
Question de recherche, 3+ graphiques avances, insights
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.shared import (
    inject_css, load_data, load_test_predictions,
    load_artifacts, LABELS, PL, C,
)

st.set_page_config(page_title="Analyse | California Housing", page_icon="🔬", layout="wide")
inject_css()

df_raw = load_data()
test_preds = load_test_predictions()
artifacts = load_artifacts()
metrics = artifacts["metrics"]
model = artifacts["model"]
base_names = artifacts["feature_names_base"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# QUESTION DE RECHERCHE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("# 🔬 Analyse approfondie")
st.markdown("")

st.markdown("""
<div class="info-box">
    <strong>Question de recherche :</strong> Quels facteurs influencent le plus le prix immobilier
    en Californie, et dans quelle mesure un modele de regression lineaire enrichi par du clustering
    geographique peut-il capturer ces relations ?
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# METRIQUES DU MODELE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="section-label">Performance du modele</div>', unsafe_allow_html=True)

pm1, pm2, pm3, pm4 = st.columns(4)
pm1.metric("R²", f"{metrics['r2']:.4f}", help="Part de variance expliquee par le modele")
pm2.metric("MAE", f"${metrics['mae']*100_000:,.0f}", help="Erreur absolue moyenne en dollars")
pm3.metric("RMSE", f"{metrics['rmse']:.4f}", help="Racine de l'erreur quadratique moyenne")
pm4.metric("Features totales", "1 010", help="8 base + 2 engineered + 1000 clusters")

st.markdown("")
st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VIZ 1 : Reel vs Predit + Residus
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if test_preds is not None:
    st.markdown('<div class="section-label">Graphique 1 — Valeurs reelles vs predites</div>', unsafe_allow_html=True)

    pred_col1, pred_col2 = st.columns(2)

    with pred_col1:
        fig_avp = go.Figure()
        fig_avp.add_trace(go.Scatter(
            x=test_preds["actual"], y=test_preds["predicted"],
            mode="markers",
            marker=dict(size=3, color=C["primary"], opacity=0.2),
            name="Predictions",
        ))
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
            title="Reel vs Predit",
            xaxis_title="Prix reel (x$100k)",
            yaxis_title="Prix predit (x$100k)",
            height=420,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        )
        st.plotly_chart(fig_avp, width="stretch")

    with pred_col2:
        fig_res = px.histogram(
            test_preds, x="residual", nbins=60,
            color_discrete_sequence=[C["success"]],
        )
        fig_res.add_vline(x=0, line_dash="dash", line_color=C["danger"], line_width=1.5)
        fig_res.update_layout(
            **PL,
            title="Distribution des residus",
            xaxis_title="Erreur (x$100k)",
            yaxis_title="Frequence",
            height=420,
            bargap=0.02,
        )
        st.plotly_chart(fig_res, width="stretch")

    st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VIZ 2 : Importance des variables (coefficients)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="section-label">Graphique 2 — Importance des variables</div>', unsafe_allow_html=True)

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
    height=400,
    title="Coefficients standardises du modele (features de base)",
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig_coef, width="stretch")

st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VIZ 3 : Residus vs Predit (pattern d'erreur)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if test_preds is not None:
    st.markdown('<div class="section-label">Graphique 3 — Analyse des residus</div>', unsafe_allow_html=True)

    fig_res_sc = go.Figure()
    fig_res_sc.add_trace(go.Scatter(
        x=test_preds["predicted"], y=test_preds["residual"],
        mode="markers",
        marker=dict(size=3, color=C["secondary"], opacity=0.2),
    ))
    fig_res_sc.add_hline(y=0, line_dash="dash", line_color=C["danger"], line_width=1.5)
    fig_res_sc.update_layout(
        **PL,
        title="Residus vs valeurs predites — detection de patterns d'erreur",
        xaxis_title="Prix predit (x$100k)",
        yaxis_title="Residu (reel - predit)",
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig_res_sc, width="stretch")

    st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PIPELINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

st.markdown("")
st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INSIGHTS & CONCLUSIONS (3-4 paragraphes)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="section-label">Insights et conclusions</div>', unsafe_allow_html=True)

st.markdown(f"""
**Resultats principaux.** Le modele de regression lineaire atteint un R² de {metrics['r2']:.4f},
ce qui signifie qu'il explique environ {metrics['r2']*100:.1f}% de la variance des prix immobiliers.
Le revenu median est de loin le predicteur le plus puissant : a lui seul, il capture la majeure
partie de la relation avec le prix. La localisation geographique, encodee via 1 000 clusters K-Means,
apporte une amelioration significative par rapport a une simple regression sur les coordonnees brutes.

**Surprises dans les donnees.** L'age des logements a un impact positif sur le prix, ce qui peut
sembler contre-intuitif. Cela s'explique par le fait que les quartiers anciens en Californie
(San Francisco, Los Angeles centre) sont souvent les plus chers. La population et le nombre
d'occupants ont un coefficient negatif : les districts surpeuples tendent a avoir des prix plus bas.

**Limites de l'analyse.** Le plafonnement des prix a $500 000 (5.0 dans le dataset) introduit une
censure a droite qui biaise le modele vers le bas pour les districts les plus chers. Le graphique
des residus montre d'ailleurs une sous-estimation systematique pour les valeurs elevees. De plus,
les donnees de 1990 ne refletent evidemment pas le marche immobilier californien actuel.

**Recommandations.** Pour ameliorer le modele, on pourrait explorer des algorithmes non-lineaires
(Random Forest, Gradient Boosting) qui captureraient mieux les interactions entre variables.
L'ajout de donnees supplementaires (proximite des transports, taux de criminalite, qualite des
ecoles) enrichirait egalement la prediction. Enfin, traiter la censure a droite avec un modele
Tobit permettrait de mieux estimer les prix dans la tranche superieure.
""")
