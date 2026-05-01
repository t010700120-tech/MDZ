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
    .block-container { padding: 2rem; }
    h1 { font-size: 1.6rem !important; font-weight: 600 !important; color: #1a1a1a !important; }
</style>
""", unsafe_allow_html=True)

CSV_FILE = "visitas.csv"

COLUMNAS = [
    "Nombre_Vendedor","Mesa","Codigo_Vendedor","Zona",
    "Fecha","Codigo_PDC","Nombre_Cliente","Giro_Negocio",
    "OREO_34GR","OREO_54GR","OREO_ROLLO","RITZ_ROLLO","RITZ_TACO",
    "CLUB_SOCIAL_TRA","CLUB_SOCIAL_SAB",
    "TRIDENT_5s","TRIDENT_EVUP","HALLS_12s","HALLS_100s","CHICLETS_2S",
    "LEGOS_GC","TOBOGAN_RITZ_OREO","EXHIB_KIWI",
    "CONT_LEGOS_GC","CONT_TOBOGAN_RITZ_OREO","CONT_EXHIB_KIWI",
    "Colocacion_Terceros",
    "Efectividad","Ticket_Promedio","Tiempo_PDC",
    "Latitud","Longitud"
]

def cargar_datos():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        return df
    return pd.DataFrame(columns=COLUMNAS)

def guardar_registro(registro):
    df = cargar_datos()
    df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

if "pagina" not in st.session_state:
    st.session_state.pagina = "formulario"

# ================= FORMULARIO =================
if st.session_state.pagina == "formulario":

    st.markdown("# 📋 Registro de Visita")
    st.markdown("---")

    with st.form("form_visita"):

        st.markdown("### 🧑‍💼 Datos del Vendedor")
        colv1, colv2, colv3 = st.columns(3)

        with colv1:
            nombre_vendedor = st.text_input("Nombre del Vendedor")

        with colv2:
            mesa = st.text_input("Mesa")

        with colv3:
            codigo_vendedor = st.text_input("Código del Vendedor")

        zona = st.text_input("Zona")

        st.markdown("---")

        st.markdown("### 👤 Datos del cliente")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            fecha = st.date_input("Fecha", value=date.today())

        with col2:
            codigo_pdc = st.text_input("Código PDC", max_chars=8)

        with col3:
            nombre_cliente = st.text_input("Cliente")

        with col4:
            giro_negocio = st.selectbox("Giro", [
                "Bodega","Minimarket","Kiosko","Especializados","Otros"
            ])

        st.markdown("---")

        st.markdown("### 📊 Indicadores")
        k1, k2, k3 = st.columns(3)

        with k1:
            efectividad = st.number_input("Ventas (S/)", min_value=0.0)

        with k2:
            ticket_promedio = st.number_input("Ticket Promedio", min_value=0.0)

        with k3:
            tiempo_pdc = st.number_input("Tiempo PDC", min_value=0)

        terceros = st.selectbox("Terceros", ["Sí","No"])

        st.markdown("### 📍 Ubicación")
        lat = st.number_input("Latitud")
        lon = st.number_input("Longitud")

        submitted = st.form_submit_button("Guardar")

        if submitted:
            registro = {
                "Nombre_Vendedor": nombre_vendedor,
                "Mesa": mesa,
                "Codigo_Vendedor": codigo_vendedor,
                "Zona": zona,
                "Fecha": fecha,
                "Codigo_PDC": codigo_pdc,
                "Nombre_Cliente": nombre_cliente,
                "Giro_Negocio": giro_negocio,
                "Efectividad": efectividad,
                "Ticket_Promedio": ticket_promedio,
                "Tiempo_PDC": tiempo_pdc,
                "Colocacion_Terceros": terceros,
                "Latitud": lat,
                "Longitud": lon
            }
            guardar_registro(registro)
            st.session_state.pagina = "dashboard"
            st.rerun()

# ================= DASHBOARD =================
else:

    df = cargar_datos()

    st.markdown("# 📊 Dashboard")

    if df.empty:
        st.warning("No hay registros aún.")
        st.stop()

    df["Efectividad"] = pd.to_numeric(df["Efectividad"], errors="coerce").fillna(0)
    df["Cierre"] = df["Efectividad"] > 0

    total_visitas = len(df)
    total_ventas = df["Efectividad"].sum()
    efectividad_pct = df["Cierre"].mean()*100

    col1, col2, col3 = st.columns(3)
    col1.metric("Visitas", total_visitas)
    col2.metric("Ventas Totales", f"S/ {total_ventas:,.2f}")
    col3.metric("Efectividad %", f"{efectividad_pct:.1f}%")

    # COBERTURA
    biscuits = ["OREO_34GR","OREO_54GR","OREO_ROLLO","RITZ_ROLLO","RITZ_TACO","CLUB_SOCIAL_TRA","CLUB_SOCIAL_SAB"]
    gomas = ["TRIDENT_5s","TRIDENT_EVUP","HALLS_12s","HALLS_100s","CHICLETS_2S"]

    df["BISCUITS"] = df[biscuits].sum(axis=1) > 0
    df["GOMAS"] = df[gomas].sum(axis=1) > 0

    st.markdown("### Cobertura")
    st.write("Biscuits:", round(df["BISCUITS"].mean()*100,1), "%")
    st.write("Gomas:", round(df["GOMAS"].mean()*100,1), "%")

    # EXHIBIDORES
    st.markdown("### Exhibidores")
    st.write("Total:", int(df[["LEGOS_GC","TOBOGAN_RITZ_OREO","EXHIB_KIWI"]].sum().sum()))
    st.write("Contaminados:", int(df[["CONT_LEGOS_GC","CONT_TOBOGAN_RITZ_OREO","CONT_EXHIB_KIWI"]].sum().sum()))

    # TERCEROS
    st.markdown("### Terceros")
    st.write(df["Colocacion_Terceros"].value_counts())

    # GIRO
    st.markdown("### Exhibidores por giro")
    df["TOTAL_EXHIB"] = df[["LEGOS_GC","TOBOGAN_RITZ_OREO","EXHIB_KIWI"]].sum(axis=1)
    st.plotly_chart(px.bar(df, x="Giro_Negocio", y="TOTAL_EXHIB"), use_container_width=True)

    # EFECTIVIDAD
    st.markdown("### Cierre por vendedor")
    cierre = df.groupby("Nombre_Vendedor")["Cierre"].mean().reset_index()
    st.plotly_chart(px.bar(cierre, x="Nombre_Vendedor", y="Cierre"), use_container_width=True)

    # MAPA
    st.markdown("### Mapa")
    if "Latitud" in df.columns:
        st.map(df.rename(columns={"Latitud":"lat","Longitud":"lon"}))

    # RANKING
    st.markdown("### Ranking vendedores")
    ranking = df.groupby("Nombre_Vendedor")["Efectividad"].sum().reset_index().sort_values(by="Efectividad", ascending=False)
    st.dataframe(ranking, use_container_width=True)

    # TABLA
    st.markdown("### Últimas visitas")
    st.dataframe(df.tail(20), use_container_width=True)

    if st.button("Nueva visita"):
        st.session_state.pagina = "formulario"
        st.rerun()
 
