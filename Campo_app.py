import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os

st.set_page_config(page_title="SUPERVISIÓN CANAL TRADICIONAL", layout="wide", page_icon="📊")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background-color: #f5f4f0; }
    .block-container { padding: 2rem 2rem 2rem 2rem; }
    h1 { font-size: 1.6rem !important; font-weight: 600 !important; color: #1a1a1a !important; }
    .kpi-box { background: white; border-radius: 12px; padding: 1.2rem 1.4rem; border: 1px solid #e8e6e0; }
    .kpi-label { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: #888; margin-bottom: 4px; }
    .kpi-value { font-size: 28px; font-weight: 600; color: #1a1a1a; }
    .kpi-sub { font-size: 12px; color: #aaa; margin-top: 2px; }
    .stButton > button { background: #1a1a1a !important; color: white !important; border: none !important;
        border-radius: 8px !important; font-weight: 500 !important; padding: .6rem 2rem !important; font-size: 15px !important; }
    .stButton > button:hover { background: #333 !important; }
    div[data-testid="stCheckbox"] label { font-size: 13px !important; }
    .leyenda-box { background: #f0efeb; border-radius: 8px; padding: .6rem 1rem; font-size: 12px; color: #555; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

CSV_FILE = "visitas.csv"

COLUMNAS = [
    "Fecha", "Codigo_PDC", "Nombre_Cliente", "Giro_Negocio",
    "OREO_34GR", "OREO_54GR", "OREO_ROLLO", "RITZ_ROLLO", "RITZ_TACO",
    "FIELD_CC", "FIELD_DP", "FIELD_VAIN", "CLUB_SOCIAL_TRA", "CLUB_SOCIAL_SAB",
    "TRIDENT_5s", "TRIDENT_EVUP", "HALLS_12s", "HALLS_100s", "CHICLETS_2S",
    "LEGOS_GC", "TOBOGAN_RITZ_OREO", "EXHIB_KIWI",
    "CONT_LEGOS_GC", "CONT_TOBOGAN_RITZ_OREO", "CONT_EXHIB_KIWI",
    "Visibilidad",
    "Colocacion_Terceros", "Marca_Tercero",
    "Efectividad", "Ticket_Promedio", "Tiempo_PDC"
]

def cargar_datos():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=COLUMNAS)

def guardar_registro(registro):
    df = cargar_datos()
    nuevo = pd.DataFrame([registro])
    df = pd.concat([df, nuevo], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

if "pagina" not in st.session_state:
    st.session_state.pagina = "formulario"

if st.session_state.pagina == "formulario":

    st.markdown("# 📋 Registro de Visita")
    st.markdown("---")

    with st.form("form_visita", clear_on_submit=False):

        st.markdown("### 👤 Datos del cliente")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            fecha = st.date_input("Fecha", value=date.today())
        with col2:
            codigo_pdc = st.text_input("Código PDC (8 dígitos)", max_chars=8)
        with col3:
            nombre_cliente = st.text_input("Nombre del Cliente")
        with col4:
            giro_negocio = st.selectbox("Giro de Negocio", options=[
                "1 - Bodega","2 - Minimarket / Tiendas","3 - Kiosko",
                "4 - Especializados","5 - Otros"
            ])

        st.markdown("---")

        st.markdown("### 👁️ Visibilidad")
        visibilidad = st.radio("Nivel de visibilidad", [1,2,3], horizontal=True)

        st.markdown("---")

        st.markdown("### 🏷️ Colocación de Terceros")
        col_terc1, col_terc2 = st.columns([1, 2])
        with col_terc1:
            colocacion_terceros = st.radio("¿Hay productos de terceros?", options=["No", "Sí"], horizontal=True)
        with col_terc2:
            marca_tercero = st.text_input("Marca del tercero (si aplica)")

        st.markdown("---")

        st.markdown("### 📊 Indicadores de la visita")
        k1, k2, k3 = st.columns(3)
        with k1:
            efectividad = st.number_input("Ventas (S/)", min_value=0.0)
        with k2:
            ticket_promedio = st.number_input("Ticket Promedio (S/)", min_value=0.0)
        with k3:
            tiempo_pdc = st.number_input("Tiempo en PDC", min_value=0)

        st.markdown("---")

        submitted = st.form_submit_button("✅ Guardar y ver dashboard →", use_container_width=True)

        if submitted:
            if not codigo_pdc or not nombre_cliente:
                st.error("Por favor completa el Código PDC y el Nombre del Cliente.")
            else:
                registro = {
                    "Fecha": str(fecha),
                    "Codigo_PDC": codigo_pdc,
                    "Nombre_Cliente": nombre_cliente,
                    "Giro_Negocio": giro_negocio,
                    "Visibilidad": visibilidad,
                    "Colocacion_Terceros": colocacion_terceros,
                    "Marca_Tercero": marca_tercero,
                    "Efectividad": efectividad,
                    "Ticket_Promedio": ticket_promedio,
                    "Tiempo_PDC": tiempo_pdc
                }
                guardar_registro(registro)
                st.session_state.pagina = "dashboard"
                st.rerun()

elif st.session_state.pagina == "dashboard":

    df = cargar_datos()
    df.fillna(0, inplace=True)

    for col in COLUMNAS:
        if col not in df.columns:
            df[col] = 0

    st.markdown("# 📊 Dashboard")

    if df.empty:
        st.warning("No hay registros aún.")
        st.stop()

    total_visitas = len(df)
    total_ventas = df["Efectividad"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Visitas", total_visitas)
    col2.metric("Total Ventas", f"S/ {total_ventas:,.2f}")

    st.markdown("### Últimas visitas")
    st.dataframe(df.tail(20), use_container_width=True)
