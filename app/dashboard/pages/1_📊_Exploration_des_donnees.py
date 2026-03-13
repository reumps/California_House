"""
California Housing — Page 2 : Exploration des Donnees
5+ visualisations, 4-6 KPIs, 2+ filtres interactifs
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.shared import inject_css, load_data, LABELS, PL, C

st.set_page_config(page_title="Exploration | California Housing", page_icon="📊", layout="wide")
inject_css()

df_raw = load_data()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR — Filtres interactifs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("### 📊 Exploration")
    st.markdown("---")
    st.markdown("**Filtres interactifs**")

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

    age_range = st.slider(
        "Age des logements (annees)",
        int(df_raw["HouseAge"].min()),
        int(df_raw["HouseAge"].max()),
        (1, 52),
        step=1,
    )

df = df_raw[
    (df_raw["MedHouseVal"] >= price_range[0]) &
    (df_raw["MedHouseVal"] <= price_range[1]) &
    (df_raw["MedInc"] >= income_range[0]) &
    (df_raw["MedInc"] <= income_range[1]) &
    (df_raw["HouseAge"] >= age_range[0]) &
    (df_raw["HouseAge"] <= age_range[1])
].copy()

with st.sidebar:
    st.markdown("---")
    st.markdown(f"**{len(df):,}** / {len(df_raw):,} districts affiches")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TITRE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("# 📊 Exploration des donnees")
st.markdown("")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6 KPIs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="section-label">Metriques cles (filtrees)</div>', unsafe_allow_html=True)

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Districts", f"{len(df):,}")
m2.metric("Prix moyen", f"${df['MedHouseVal'].mean() * 100_000:,.0f}")
m3.metric("Prix median", f"${df['MedHouseVal'].median() * 100_000:,.0f}")
m4.metric("Revenu moyen", f"${df['MedInc'].mean() * 10_000:,.0f}")
m5.metric("Age moyen", f"{df['HouseAge'].mean():.0f} ans")
m6.metric("Population totale", f"{df['Population'].sum():,.0f}")

st.markdown("")
st.markdown("---")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VIZ 1 : Distribution de la variable cible
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="section-label">Visualisation 1 — Distribution des prix</div>', unsafe_allow_html=True)

fig_dist = px.histogram(
    df, x="MedHouseVal", nbins=60,
    color_discrete_sequence=[C["primary"]],
    labels=LABELS,
)
fig_dist.update_layout(
    **PL,
    title="Distribution du prix median des logements",
    xaxis_title="Prix median (x$100k)",
    yaxis_title="Nombre de districts",
    bargap=0.02,
    height=400,
)
st.plotly_chart(fig_dist, width="stretch")

st.markdown("""
<div class="info-box">
    On observe un pic autour de $100k-$200k et une accumulation a $500k (prix plafonne dans le dataset).
    Cette censure a droite est une limite connue du dataset.
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VIZ 2 : Carte geographique (comparaison entre groupes/regions)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="section-label">Visualisation 2 — Carte geographique des prix</div>', unsafe_allow_html=True)

map_col1, map_col2 = st.columns([4, 1])

with map_col2:
    map_color = st.selectbox(
        "Colorer par",
        ["MedHouseVal", "MedInc", "HouseAge", "Population"],
        format_func=lambda x: LABELS.get(x, x),
        key="map_color",
    )
    map_n = st.slider("Points", 2000, min(len(df), 15000), min(6000, len(df)), 500)

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

st.markdown("---")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VIZ 3 : Scatter plot — Revenu vs Prix
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="section-label">Visualisation 3 — Relation Revenu / Prix</div>', unsafe_allow_html=True)

df_scatter = df.sample(n=min(5000, len(df)), random_state=42)

fig_scatter = px.scatter(
    df_scatter,
    x="MedInc", y="MedHouseVal",
    color="HouseAge",
    color_continuous_scale="Viridis",
    opacity=0.4,
    labels=LABELS,
    hover_data={"Population": ":,.0f"},
)
fig_scatter.update_layout(
    **PL,
    title="Prix median vs Revenu median (colore par age du logement)",
    xaxis_title="Revenu median (x$10k)",
    yaxis_title="Prix median (x$100k)",
    height=450,
    coloraxis_colorbar=dict(title=dict(text="Age", font=dict(size=11)), thickness=12),
)
st.plotly_chart(fig_scatter, width="stretch")

st.markdown("""
<div class="info-box">
    Le <strong>revenu median</strong> est le meilleur predicteur du prix (r = 0.69).
    On observe clairement que les districts a haut revenu ont des prix plus eleves.
    Le plafonnement a 5.0 (500k$) est visible sur le bord superieur.
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VIZ 4 : Heatmap de correlations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="section-label">Visualisation 4 — Correlations entre variables</div>', unsafe_allow_html=True)

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
    title="Matrice de correlation",
    coloraxis_colorbar=dict(title="r", thickness=12),
)
fig_corr.update_traces(textfont=dict(size=11))
st.plotly_chart(fig_corr, width="stretch")

st.markdown("---")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VIZ 5 : Box plot — Prix par tranche d'age
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="section-label">Visualisation 5 — Prix par tranche d\'age</div>', unsafe_allow_html=True)

df_box = df.copy()
df_box["Tranche_age"] = pd.cut(
    df_box["HouseAge"],
    bins=[0, 10, 20, 30, 40, 52],
    labels=["0-10 ans", "11-20 ans", "21-30 ans", "31-40 ans", "41-52 ans"],
)

fig_box = px.box(
    df_box,
    x="Tranche_age",
    y="MedHouseVal",
    color="Tranche_age",
    color_discrete_sequence=[C["primary"], C["secondary"], C["success"], C["warning"], C["danger"]],
    labels={"Tranche_age": "Tranche d'age", "MedHouseVal": "Prix median (x$100k)"},
)
fig_box.update_layout(
    **PL,
    title="Distribution des prix par tranche d'age des logements",
    height=420,
    showlegend=False,
)
st.plotly_chart(fig_box, width="stretch")

st.markdown("---")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VIZ 6 (Bonus) : Distribution variable au choix
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="section-label">Visualisation 6 — Distribution au choix</div>', unsafe_allow_html=True)

dist_col1, dist_col2 = st.columns([3, 1])
with dist_col2:
    dist_var = st.selectbox(
        "Variable",
        df.columns.tolist(),
        format_func=lambda x: LABELS.get(x, x),
        key="dist_var",
    )

fig_hist = px.histogram(
    df, x=dist_var, nbins=60,
    color_discrete_sequence=[C["secondary"]],
)
fig_hist.update_layout(
    **PL,
    title=LABELS.get(dist_var, dist_var),
    xaxis_title="",
    yaxis_title="Districts",
    bargap=0.02,
    height=380,
)
with dist_col1:
    st.plotly_chart(fig_hist, width="stretch")

with st.expander("Voir les statistiques detaillees"):
    st.dataframe(
        df.describe().round(2).rename(columns=LABELS),
        width="stretch",
    )
