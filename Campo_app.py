import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os

# ================= CONFIG =================
st.set_page_config(page_title="SUPERVISIÓN CANAL TRADICIONAL", layout="wide", page_icon="📊")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CSV_FILE = "visitas.csv"

# ================= COLUMNAS =================
COLUMNAS = [
    "Nombre_Vendedor","Mesa","Codigo_Vendedor","Latitud","Longitud",
    "Fecha","Codigo_PDC","Nombre_Cliente","Giro_Negocio",
    "OREO_34GR","OREO_54GR","OREO_ROLLO","RITZ_ROLLO","RITZ_TACO",
    "FIELD_CC","FIELD_DP","FIELD_VAIN","CLUB_SOCIAL_TRA","CLUB_SOCIAL_SAB",
    "TRIDENT_5s","TRIDENT_EVUP","HALLS_12s","HALLS_100s","CHICLETS_2S",
    "LEGOS_GC","TOBOGAN_RITZ_OREO","EXHIB_KIWI",
    "CONT_LEGOS_GC","CONT_TOBOGAN_RITZ_OREO","CONT_EXHIB_KIWI",
    "Tiene_Exhibidores","Tiene_Contaminacion",
    "Visibilidad",
    "Colocacion_Terceros","Marca_Tercero",
    "Comentario","Foto",
    "Efectividad","Ticket_Promedio","Tiempo_PDC"
]

# ================= FUNCIONES =================
def cargar_datos():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=COLUMNAS)

def guardar_registro(registro):
    df = cargar_datos()
    df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def convertir_excel(df):
    return df.to_csv(index=False).encode('utf-8')

# ================= ESTADO =================
if "pagina" not in st.session_state:
    st.session_state.pagina = "formulario"

# ================= FORMULARIO =================
if st.session_state.pagina == "formulario":

    st.markdown("# 📋 Registro de Visita")

    with st.form("form_visita"):

        # VENDEDOR
        st.markdown("### 🧑‍💼 Datos del Vendedor")
        v1,v2,v3,v4,v5 = st.columns(5)
        nombre_vendedor = v1.text_input("Nombre")
        mesa = v2.text_input("Mesa")
        codigo_vendedor = v3.text_input("Código")
        latitud = v4.text_input("Latitud")
        longitud = v5.text_input("Longitud")

        st.markdown("---")

        # CLIENTE
        st.markdown("### 👤 Datos del cliente")
        c1,c2,c3,c4 = st.columns(4)
        fecha = c1.date_input("Fecha", value=date.today())
        codigo_pdc = c2.text_input("Código PDC")
        nombre_cliente = c3.text_input("Cliente")
        giro = c4.selectbox("Giro", ["Bodega","Minimarket","Kiosko","Otros"])

        st.markdown("---")

        # BISCUITS
        st.markdown("### 🍪 Presencia Biscuits")
        biscuits = ["OREO_34GR","OREO_54GR","OREO_ROLLO","RITZ_ROLLO","RITZ_TACO",
                    "FIELD_CC","FIELD_DP","FIELD_VAIN","CLUB_SOCIAL_TRA","CLUB_SOCIAL_SAB"]
        biscuits_vals = {b: st.checkbox(b) for b in biscuits}

        st.markdown("---")

        # G&C
        st.markdown("### 🍬 Presencia G&C")
        gyc = ["TRIDENT_5s","TRIDENT_EVUP","HALLS_12s","HALLS_100s","CHICLETS_2S"]
        gyc_vals = {g: st.checkbox(g) for g in gyc}

        st.markdown("---")

        # EXHIBIDORES
        st.markdown("### 🏪 Exhibidores")
        tiene_exhibidores = st.radio("¿Tiene exhibidores?", ["No","Sí"], horizontal=True)

        tipos = ["LEGOS_GC","TOBOGAN_RITZ_OREO","EXHIB_KIWI"]
        tipos_vals = {t: st.checkbox(t) for t in tipos}

        st.markdown("### ⚠️ Contaminación")
        tiene_contaminacion = st.radio("¿Hay contaminación?", ["No","Sí"], horizontal=True)

        cont = ["CONT_LEGOS_GC","CONT_TOBOGAN_RITZ_OREO","CONT_EXHIB_KIWI"]
        cont_vals = {c: st.checkbox(c) for c in cont}

        foto = None
        comentario = ""

        if tiene_exhibidores == "Sí":
            foto = st.file_uploader("📸 Subir foto", type=["jpg","png","jpeg"])
            comentario = st.text_area("Comentario")

        st.markdown("---")

        visibilidad = st.radio("Visibilidad", [1,2,3], horizontal=True)

        col_ter = st.radio("¿Hay terceros?", ["No","Sí"], horizontal=True)
        marca = st.text_input("Marca tercero")

        st.markdown("---")

        k1,k2,k3 = st.columns(3)
        efectividad = k1.number_input("Efectividad", min_value=0)
        ticket = k2.number_input("Ticket Promedio", min_value=0.0)
        tiempo = k3.number_input("Tiempo", min_value=0)

        submitted = st.form_submit_button("📊 Guardar y ver Dashboard")

        if submitted:

            ruta_foto = ""
            if foto:
                ruta_foto = os.path.join(UPLOAD_FOLDER, foto.name)
                with open(ruta_foto,"wb") as f:
                    f.write(foto.getbuffer())

            registro = {
                "Nombre_Vendedor":nombre_vendedor,
                "Mesa":mesa,
                "Codigo_Vendedor":codigo_vendedor,
                "Latitud":latitud,
                "Longitud":longitud,
                "Fecha":str(fecha),
                "Codigo_PDC":codigo_pdc,
                "Nombre_Cliente":nombre_cliente,
                "Giro_Negocio":giro,
                **{k:int(v) for k,v in biscuits_vals.items()},
                **{k:int(v) for k,v in gyc_vals.items()},
                **{k:int(v) for k,v in tipos_vals.items()},
                **{k:int(v) for k,v in cont_vals.items()},
                "Tiene_Exhibidores":tiene_exhibidores,
                "Tiene_Contaminacion":tiene_contaminacion,
                "Visibilidad":visibilidad,
                "Colocacion_Terceros":col_ter,
                "Marca_Tercero":marca,
                "Comentario":comentario,
                "Foto":ruta_foto,
                "Efectividad":efectividad,
                "Ticket_Promedio":ticket,
                "Tiempo_PDC":tiempo
            }

            guardar_registro(registro)
            st.success("✅ Registro guardado correctamente")
            st.session_state.pagina = "dashboard"
            st.rerun()

# ================= DASHBOARD =================
elif st.session_state.pagina == "dashboard":

    st.markdown("# 📊 Dashboard - Supervisión Canal Tradicional")

    if st.button("➕ Nueva visita"):
        st.session_state.pagina = "formulario"
        st.rerun()

    df = cargar_datos()

    if df.empty:
        st.warning("No hay registros aún.")
        st.stop()

    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Efectividad"] = pd.to_numeric(df["Efectividad"], errors="coerce").fillna(0)
    df["Ticket_Promedio"] = pd.to_numeric(df["Ticket_Promedio"], errors="coerce").fillna(0)
    df["Tiempo_PDC"] = pd.to_numeric(df["Tiempo_PDC"], errors="coerce").fillna(0)

    # KPIs
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📍 Visitas", len(df))
    c2.metric("💰 Ventas", int(df["Efectividad"].sum()))
    c3.metric("🧾 Ticket", f"S/ {df['Ticket_Promedio'].mean():.2f}")
    c4.metric("⏱️ Tiempo", f"{df['Tiempo_PDC'].mean():.0f} min")

    st.markdown("---")

    # DESCARGA
    st.markdown("### 📥 Descargar información")
    st.download_button(
        "⬇️ Descargar en Excel",
        convertir_excel(df),
        file_name=f"reporte_visitas_{date.today()}.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # GRÁFICOS
    g1,g2 = st.columns(2)

    with g1:
        fig1 = px.bar(df.groupby("Fecha")["Efectividad"].sum().reset_index(),
                      x="Fecha", y="Efectividad")
        st.plotly_chart(fig1, use_container_width=True)

    with g2:
        fig2 = px.pie(df["Giro_Negocio"].value_counts().reset_index(),
                      names="Giro_Negocio", values="count")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # MAPA
    df_map = df.dropna(subset=["Latitud","Longitud"])
    if not df_map.empty:
        df_map["Latitud"] = pd.to_numeric(df_map["Latitud"], errors="coerce")
        df_map["Longitud"] = pd.to_numeric(df_map["Longitud"], errors="coerce")
        st.map(df_map.rename(columns={"Latitud":"lat","Longitud":"lon"}))

    st.markdown("---")

    # FOTOS
    st.markdown("### 📸 Evidencias")
    for _, row in df.tail(5).iterrows():
        if row["Foto"]:
            st.image(row["Foto"], width=250)
            st.caption(row["Comentario"])

    st.markdown("---")

    st.dataframe(df.tail(20), use_container_width=True)
