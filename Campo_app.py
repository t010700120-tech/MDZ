import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import os
 
st.set_page_config(page_title="MDZ - Registro de Visitas", layout="wide", page_icon="📊")
 
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background-color: #f5f4f0; }
    .block-container { padding: 2rem 2rem 2rem 2rem; }
    h1 { font-size: 1.6rem !important; font-weight: 600 !important; color: #1a1a1a !important; }
    h2 { font-size: 1.1rem !important; font-weight: 500 !important; color: #333 !important; }
    .kpi-box { background: white; border-radius: 12px; padding: 1.2rem 1.4rem; border: 1px solid #e8e6e0; }
    .kpi-label { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: #888; margin-bottom: 4px; }
    .kpi-value { font-size: 28px; font-weight: 600; color: #1a1a1a; }
    .kpi-sub { font-size: 12px; color: #aaa; margin-top: 2px; }
    .section-card { background: white; border-radius: 14px; padding: 1.5rem; border: 1px solid #e8e6e0; margin-bottom: 1rem; }
    .stButton > button { background: #1a1a1a !important; color: white !important; border: none !important;
        border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important; padding: .6rem 2rem !important; font-size: 15px !important; }
    .stButton > button:hover { background: #333 !important; }
    div[data-testid="stCheckbox"] label { font-size: 13px !important; }
    .producto-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
</style>
""", unsafe_allow_html=True)
 
CSV_FILE = "visitas.csv"
 
COLUMNAS = [
    "Fecha", "Codigo_PDC", "Nombre_Cliente",
    "OREO_34GR", "OREO_54GR", "OREO_ROLLO", "RITZROLLO", "RITZ_TACO",
    "FIELD_CC", "FIELD_DP", "FIELD_TAIN", "CLUB_SOCIAL_TRA", "CLUB_SOCIAL_SAB",
    "TRIDENT_STUN", "TRIDENT_EYUP",
    "HALLS_1025", "HALLS_MSL", "HALLS_SISTEMAS", "CHICLETS_25",
    "LEGOS_GBC", "TOBOGAN_FINA_OREO", "EXHIB_KIWI",
    "ExhibPOP_Oport", "Esb_Legos", "Esb_Tobogas", "Esb_Kiwi", "ExhibPOP_Kiwi_Oport",
    "Ubicacion_Preferencial", "Colocacion_Terceros",
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
 
# --- NAVEGACIÓN ---
if "pagina" not in st.session_state:
    st.session_state.pagina = "formulario"
 
# ═══════════════════════════════════════════
# PÁGINA: FORMULARIO
# ═══════════════════════════════════════════
if st.session_state.pagina == "formulario":
 
    st.markdown("# 📋 Registro de Visita")
    st.markdown("---")
 
    with st.form("form_visita", clear_on_submit=False):
 
        # --- DATOS BÁSICOS ---
        st.markdown("### 👤 Datos del cliente")
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha = st.date_input("Fecha", value=date.today())
        with col2:
            codigo_pdc = st.text_input("Código PDC (3 dígitos)", max_chars=10, placeholder="Ej: 001")
        with col3:
            nombre_cliente = st.text_input("Nombre del Cliente", placeholder="Ej: Bodega Central")
 
        st.markdown("---")
 
        # --- PRESENCIA BISCUITS ---
        st.markdown("### 🍪 Presencia Biscuits")
        biscuits = {
            "OREO_34GR": "OREO 34GR", "OREO_54GR": "OREO 54GR", "OREO_ROLLO": "OREO ROLLO",
            "RITZROLLO": "RITZ ROLLO", "RITZ_TACO": "RITZ TACO",
            "FIELD_CC": "FIELD (CC)", "FIELD_DP": "FIELD (DP)", "FIELD_TAIN": "FIELD (TAIN)",
            "CLUB_SOCIAL_TRA": "CLUB SOCIAL (TRA)", "CLUB_SOCIAL_SAB": "CLUB SOCIAL (SAB)"
        }
        cols = st.columns(5)
        biscuits_vals = {}
        for i, (key, label) in enumerate(biscuits.items()):
            with cols[i % 5]:
                biscuits_vals[key] = st.checkbox(label, key=f"b_{key}")
 
        st.markdown("---")
 
        # --- PRESENCIA G&C ---
        st.markdown("### 🍬 Presencia G&C")
        gyc = {
            "TRIDENT_STUN": "TRIDENT S/TUN", "TRIDENT_EYUP": "TRIDENT EYUP",
            "HALLS_1025": "HALLS 1025", "HALLS_MSL": "HALLS MSL",
            "HALLS_SISTEMAS": "HALLS Sistemas", "CHICLETS_25": "CHICLETS 25"
        }
        cols2 = st.columns(6)
        gyc_vals = {}
        for i, (key, label) in enumerate(gyc.items()):
            with cols2[i % 6]:
                gyc_vals[key] = st.checkbox(label, key=f"g_{key}")
 
        st.markdown("---")
 
        # --- TIPOS DE EXHIBIDORES ---
        st.markdown("### 🏪 Tipos de Exhibidores")
        tipos = {
            "LEGOS_GBC": "LEGOS (GBC)", "TOBOGAN_FINA_OREO": "TOBOGÁN (Fina/Oreo)", "EXHIB_KIWI": "EXHIB KIWI"
        }
        cols3 = st.columns(3)
        tipos_vals = {}
        for i, (key, label) in enumerate(tipos.items()):
            with cols3[i]:
                tipos_vals[key] = st.checkbox(label, key=f"t_{key}")
 
        st.markdown("---")
 
        # --- EXHIBIDORES POP ---
        st.markdown("### 🎯 Exhibidores / Contaminación / Visibilidad")
        exhib = {
            "ExhibPOP_Oport": "Exhib POP Oportunidad", "Esb_Legos": "Esb. Legos",
            "Esb_Tobogas": "Esb. Tobogán", "Esb_Kiwi": "Esb. Kiwi",
            "ExhibPOP_Kiwi_Oport": "Exhib POP Kiwi Oport.", "Ubicacion_Preferencial": "Ubicación Preferencial",
            "Colocacion_Terceros": "Colocación Terceros"
        }
        cols4 = st.columns(4)
        exhib_vals = {}
        for i, (key, label) in enumerate(exhib.items()):
            with cols4[i % 4]:
                exhib_vals[key] = st.checkbox(label, key=f"e_{key}")
 
        st.markdown("---")
 
        # --- KPIs NUMÉRICOS ---
        st.markdown("### 📊 Indicadores de la visita")
        k1, k2, k3 = st.columns(3)
        with k1:
            efectividad = st.number_input("Efectividad (ventas realizadas)", min_value=0, step=1, value=0)
        with k2:
            ticket_promedio = st.number_input("Ticket Promedio (S/)", min_value=0.0, step=0.5, value=0.0, format="%.2f")
        with k3:
            tiempo_pdc = st.number_input("Tiempo en PDC (minutos)", min_value=0, step=1, value=0)
 
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
                    **{k: int(v) for k, v in biscuits_vals.items()},
                    **{k: int(v) for k, v in gyc_vals.items()},
                    **{k: int(v) for k, v in tipos_vals.items()},
                    **{k: int(v) for k, v in exhib_vals.items()},
                    "Efectividad": efectividad,
                    "Ticket_Promedio": ticket_promedio,
                    "Tiempo_PDC": tiempo_pdc
                }
                guardar_registro(registro)
                st.session_state.pagina = "dashboard"
                st.rerun()
 
# ═══════════════════════════════════════════
# PÁGINA: DASHBOARD
# ═══════════════════════════════════════════
elif st.session_state.pagina == "dashboard":
 
    df = cargar_datos()
 
    col_title, col_btn = st.columns([5, 1])
    with col_title:
        st.markdown("# 📊 Dashboard MDZ")
    with col_btn:
        if st.button("＋ Nueva visita"):
            st.session_state.pagina = "formulario"
            st.rerun()
 
    if df.empty:
        st.warning("No hay registros aún.")
        st.stop()
 
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Efectividad"] = pd.to_numeric(df["Efectividad"], errors="coerce").fillna(0)
    df["Ticket_Promedio"] = pd.to_numeric(df["Ticket_Promedio"], errors="coerce").fillna(0)
    df["Tiempo_PDC"] = pd.to_numeric(df["Tiempo_PDC"], errors="coerce").fillna(0)
 
    # KPIs
    total_visitas = len(df)
    total_ventas = df["Efectividad"].sum()
    ticket_prom = df["Ticket_Promedio"].mean()
    tiempo_prom = df["Tiempo_PDC"].mean()
 
    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-label">Total visitas</div>
            <div class="kpi-value">{total_visitas}</div>
            <div class="kpi-sub">registros</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-label">Total ventas</div>
            <div class="kpi-value">{int(total_ventas)}</div>
            <div class="kpi-sub">efectividad acumulada</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-label">Ticket promedio</div>
            <div class="kpi-value">S/ {ticket_prom:.2f}</div>
            <div class="kpi-sub">promedio por visita</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-box">
            <div class="kpi-label">Tiempo en PDC</div>
            <div class="kpi-value">{tiempo_prom:.0f} min</div>
            <div class="kpi-sub">promedio por visita</div></div>""", unsafe_allow_html=True)
 
    st.markdown("---")
 
    # GRÁFICAS
    col_g1, col_g2 = st.columns(2)
 
    with col_g1:
        st.markdown("#### Efectividad por fecha")
        df_fecha = df.groupby("Fecha")["Efectividad"].sum().reset_index()
        fig1 = px.bar(df_fecha, x="Fecha", y="Efectividad",
                      color_discrete_sequence=["#1a1a1a"])
        fig1.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           font_family="DM Sans", margin=dict(t=20, b=20))
        st.plotly_chart(fig1, use_container_width=True)
 
    with col_g2:
        st.markdown("#### Tiempo promedio por cliente (top 10)")
        df_top = df.groupby("Nombre_Cliente")["Tiempo_PDC"].mean().nlargest(10).reset_index()
        fig2 = px.bar(df_top, x="Tiempo_PDC", y="Nombre_Cliente", orientation="h",
                      color_discrete_sequence=["#555"])
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           font_family="DM Sans", margin=dict(t=20, b=20), yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)
 
    # PRESENCIA DE PRODUCTOS
    st.markdown("#### Presencia de productos (% de visitas con presencia)")
    productos = [
        "OREO_34GR","OREO_54GR","OREO_ROLLO","RITZROLLO","RITZ_TACO",
        "FIELD_CC","FIELD_DP","TRIDENT_STUN","HALLS_1025","CHICLETS_25"
    ]
    presencia_pct = []
    for p in productos:
        if p in df.columns:
            pct = df[p].astype(float).mean() * 100
            presencia_pct.append({"Producto": p.replace("_", " "), "Presencia %": round(pct, 1)})
 
    df_pres = pd.DataFrame(presencia_pct).sort_values("Presencia %", ascending=True)
    fig3 = px.bar(df_pres, x="Presencia %", y="Producto", orientation="h",
                  color="Presencia %", color_continuous_scale=["#e8e6e0", "#1a1a1a"],
                  range_x=[0, 100])
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                       font_family="DM Sans", margin=dict(t=10, b=20),
                       coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)
 
    # TABLA DE REGISTROS
    st.markdown("#### Últimas visitas")
    st.dataframe(
        df[["Fecha", "Codigo_PDC", "Nombre_Cliente", "Efectividad", "Ticket_Promedio", "Tiempo_PDC"]]
        .sort_values("Fecha", ascending=False)
        .head(20)
        .reset_index(drop=True),
        use_container_width=True
    )
