import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os

st.set_page_config(page_title="SUPERVISIÓN CANAL TRADICIONAL", layout="wide")

CSV_FILE = "visitas.csv"

COLUMNAS = [
    "Nombre_Vendedor","Zona","Mesa","Codigo_Vendedor",
    "Fecha","Codigo_PDC","Nombre_Cliente","Giro_Negocio",
    "Ventas","Ticket_Promedio","Tiempo_PDC",
    "BISCUITS","GOMAS_GYC",
    "EXHIBIDORES","EXHIBIDORES_CONTAMINADOS",
    "TERCEROS",
    "Latitud","Longitud"
]

# ================= FUNCIONES =================
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

# ================= FORMULARIO =================
if "pagina" not in st.session_state:
    st.session_state.pagina = "formulario"

if st.session_state.pagina == "formulario":

    st.title("📋 Registro de Visita")

    with st.form("form"):

        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("Vendedor")
            zona = st.text_input("Zona")

        with col2:
            lat = st.number_input("Latitud")
            lon = st.number_input("Longitud")

        fecha = st.date_input("Fecha", value=date.today())
        cliente = st.text_input("Cliente")
        giro = st.selectbox("Giro", ["Bodega","Minimarket","Kiosko","Otros"])

        st.subheader("Ventas")
        ventas = st.number_input("Ventas (S/)", min_value=0.0)
        ticket = st.number_input("Ticket Promedio", min_value=0.0)

        st.subheader("Cobertura")
        biscuits = st.checkbox("Biscuits")
        gomas = st.checkbox("Gomas y Caramelos")

        st.subheader("Exhibidores")
        exhib = st.number_input("Total Exhibidores", min_value=0)
        contaminados = st.number_input("Contaminados", min_value=0)

        terceros = st.selectbox("Colocación terceros", ["Sí","No"])

        submit = st.form_submit_button("Guardar")

        if submit:
            registro = {
                "Nombre_Vendedor": nombre,
                "Zona": zona,
                "Fecha": fecha,
                "Nombre_Cliente": cliente,
                "Giro_Negocio": giro,
                "Ventas": ventas,
                "Ticket_Promedio": ticket,
                "BISCUITS": int(biscuits),
                "GOMAS_GYC": int(gomas),
                "EXHIBIDORES": exhib,
                "EXHIBIDORES_CONTAMINADOS": contaminados,
                "TERCEROS": terceros,
                "Latitud": lat,
                "Longitud": lon
            }
            guardar_registro(registro)
            st.session_state.pagina = "dashboard"
            st.rerun()

# ================= DASHBOARD =================
else:

    df = cargar_datos()

    st.title("📊 Dashboard Comercial")

    if df.empty:
        st.warning("Sin datos")
        st.stop()

    # ================= KPIs =================
    total_visitas = len(df)
    total_ventas = df["Ventas"].sum()

    # EFECTIVIDAD (ventas > 0)
    df["Cierre"] = df["Ventas"] > 0
    efectividad = df["Cierre"].mean() * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Visitas", total_visitas)
    col2.metric("Ventas Totales", f"S/ {total_ventas:,.2f}")
    col3.metric("Efectividad %", f"{efectividad:.1f}%")

    # ================= COBERTURA =================
    st.subheader("Cobertura por categoría")

    cobertura_biscuits = df["BISCUITS"].mean() * 100
    cobertura_gomas = df["GOMAS_GYC"].mean() * 100

    st.write(f"🍪 Biscuits: {cobertura_biscuits:.1f}%")
    st.write(f"🍬 Gomas y Caramelos: {cobertura_gomas:.1f}%")

    # ================= EXHIBIDORES =================
    st.subheader("Exhibidores")

    total_exhib = df["EXHIBIDORES"].sum()
    contaminados = df["EXHIBIDORES_CONTAMINADOS"].sum()

    st.write(f"Total: {total_exhib}")
    st.write(f"Contaminados: {contaminados}")

    # ================= TERCEROS =================
    st.subheader("Colocación terceros")

    terceros_count = df["TERCEROS"].value_counts()

    fig_terceros = px.pie(names=terceros_count.index, values=terceros_count.values)
    st.plotly_chart(fig_terceros)

    # ================= GIRO VS EXHIBIDORES =================
    st.subheader("Exhibidores por giro")

    fig_giro = px.bar(df, x="Giro_Negocio", y="EXHIBIDORES")
    st.plotly_chart(fig_giro)

    # ================= EFECTIVIDAD =================
    st.subheader("Cierre de ventas")

    cierre_df = df.groupby("Nombre_Vendedor")["Cierre"].mean().reset_index()

    fig_efectividad = px.bar(cierre_df, x="Nombre_Vendedor", y="Cierre")
    st.plotly_chart(fig_efectividad)

    # ================= MAPA =================
    st.subheader("Mapa de visitas")

    if "Latitud" in df.columns:
        st.map(df.rename(columns={"Latitud":"lat","Longitud":"lon"}))

    # ================= BOTÓN =================
    if st.button("Nueva visita"):
        st.session_state.pagina = "formulario"
        st.rerun()
 
 
