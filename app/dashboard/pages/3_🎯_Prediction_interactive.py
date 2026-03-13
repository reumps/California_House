"""
California Housing — Page 4 (Bonus) : Prediction Interactive
Formulaire de prediction + comparaison de districts
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

from components.shared import (
    inject_css, load_data, load_artifacts, LABELS, PL, C,
)
from app.core.model_loader import predict

st.set_page_config(page_title="Prediction | California Housing", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")
inject_css()

df_raw = load_data()
artifacts = load_artifacts()
metrics = artifacts["metrics"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GEOCODING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@st.cache_data(ttl=3600, show_spinner=False)
def geocode_address(address: str):
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
# TITRE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("# 🎯 Prediction interactive")
st.markdown("")

st.markdown("""
<div class="info-box">
    Ajustez les caracteristiques d'un district californien pour obtenir une estimation
    du prix median des logements. Le modele utilise 1 010 features incluant le clustering
    geographique.
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FORMULAIRE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
form_left, form_spacer, form_right = st.columns([5, 0.5, 5])

with form_left:
    st.markdown('<div class="section-label">Economie & population</div>', unsafe_allow_html=True)
    med_inc = st.number_input("Revenu median du quartier (x$10k)", min_value=0.5, max_value=15.0, value=3.87, step=0.1, format="%.2f")
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
)

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
        st.error("Service de geocodage temporairement indisponible.")
    else:
        st.warning("Adresse introuvable. Verifiez l'orthographe.")

# Carte
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

with st.expander("Ajuster manuellement les coordonnees"):
    manual_col1, manual_col2 = st.columns(2)
    with manual_col1:
        latitude = st.number_input("Latitude", min_value=32.0, max_value=42.0, value=latitude, step=0.01, format="%.4f", key="pred_lat")
    with manual_col2:
        longitude = st.number_input("Longitude", min_value=-125.0, max_value=-114.0, value=longitude, step=0.01, format="%.4f", key="pred_lon")

st.markdown("")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PREDICTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if st.button("Estimer le prix", type="primary", use_container_width=True):

    input_data = {
        "MedInc": med_inc, "HouseAge": float(house_age),
        "AveRooms": ave_rooms, "AveBedrms": ave_bedrms,
        "Population": float(population), "AveOccup": ave_occup,
        "Latitude": latitude, "Longitude": longitude,
    }

    with st.spinner("Calcul en cours..."):
        price = predict(input_data)
        price_dollars = price * 100_000
        mae_dollars = metrics["mae"] * 100_000

    st.markdown(f"""
    <div class="hero-result">
        <div class="label">Prix median estime</div>
        <div class="price">${price_dollars:,.0f}</div>
        <div class="margin">Marge d'erreur : <span>+/- ${mae_dollars:,.0f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3)
    r1.metric("Valeur brute", f"{price:.3f} x$100k")
    r2.metric("Erreur moyenne (MAE)", f"${mae_dollars:,.0f}")
    r3.metric("Fiabilite du modele", f"{metrics['r2']*100:.0f}%")

    st.markdown("")

    # Position dans la distribution
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
        **PL, height=320,
        title=f"Votre estimation se situe au {percentile:.0f}e percentile",
        xaxis_title="Prix median (x$100k)",
        yaxis_title="Nombre de districts",
        bargap=0.02,
    )
    st.plotly_chart(fig_pos, width="stretch")
