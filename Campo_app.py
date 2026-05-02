import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import os

st.set_page_config(page_title="SUPERVISIÓN CANAL TRADICIONAL", layout="wide", page_icon="📊")

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
    .stButton > button { background: #1a1a1a !important; color: white !important; border: none !important;
        border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important; padding: .6rem 2rem !important; font-size: 15px !important; }
    .stButton > button:hover { background: #333 !important; }
    div[data-testid="stCheckbox"] label { font-size: 13px !important; }
    .leyenda-box { background: #f0f0eb; border-radius: 8px; padding: .5rem 1rem; font-size: 12px; color: #666; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

CSV_FILE = "visitas.csv"

COLUMNAS = [
    "Fecha", "Codigo_PDC", "Nombre_Cliente", "Giro_Negocio",
    "OREO_34GR", "OREO_54GR", "OREO_ROLLO", "RITZ_ROLLO", "RITZ_TACO",
    "FIELD_CC", "FIELD_DP", "FIELD_VAIN", "CLUB_SOCIAL_TRA", "CLUB_SOCIAL_SAB",
    "TRIDENT_5s", "TRIDENT_EVUP",
    "HALLS_12s", "HALLS_100s", "CHICLETS_2S",
    "LEGOS_GC", "TOBOGAN_RITZ_OREO", "EXHIB_KIWI",
    "CONT_LEGOS_GC", "CONT_TOBOGAN_RITZ_OREO", "CONT_EXHIB_KIWI",
    "Esb_Legos", "Esb_Tobogan", "Esb_Kiwi",
    "ExhibPOP_Oport", "ExhibPOP_Kiwi_Oport", "Ubicacion_Preferencial",
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

# ═══════════════════════════════════════════
# PÁGINA: FORMULARIO
# ═══════════════════════════════════════════
if st.session_state.pagina == "formulario":

    st.markdown("# 📋 Registro de Visita")
    st.markdown("---")

    with st.form("form_visita", clear_on_submit=False):

        # --- DATOS BÁSICOS ---
        st.markdown("### 👤 Datos del cliente")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            fecha = st.date_input("Fecha", value=date.today())
        with col2:
            codigo_pdc = st.text_input("Código PDC (8 dígitos)", max_chars=8, placeholder="Ej: 00000001")
        with col3:
            nombre_cliente = st.text_input("Nombre del Cliente", placeholder="Ej: Bodega Central")
        with col4:
            giro_negocio = st.selectbox("Giro de Negocio", [
                "Selecciona...",
                "1 - Bodega",
                "2 - Minimarket / Tiendas",
                "3 - Kiosko",
                "4 - Especializados (Panificadora, Horeca, Internet...)",
                "5 - Otros (Puesto de mercado, Centros Educativos...)"
            ])

        st.markdown("---")

        # --- PRESENCIA BISCUITS ---
        st.markdown("### 🍪 Presencia Biscuits")
        biscuits = {
            "OREO_34GR": "OREO 34GR", "OREO_54GR": "OREO 54GR", "OREO_ROLLO": "OREO ROLLO",
            "RITZ_ROLLO": "RITZ ROLLO", "RITZ_TACO": "RITZ TACO",
            "FIELD_CC": "FIELD (CC)", "FIELD_DP": "FIELD (DP)", "FIELD_VAIN": "FIELD (VAIN)",
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
            "TRIDENT_5s": "TRIDENT 5s", "TRIDENT_EVUP": "TRIDENT EVUP",
            "HALLS_12s": "HALLS 12s", "HALLS_100s": "HALLS 100s",
            "CHICLETS_2S": "CHICLETS 2S"
        }
        cols2 = st.columns(5)
        gyc_vals = {}
        for i, (key, label) in enumerate(gyc.items()):
            with cols2[i % 5]:
                gyc_vals[key] = st.checkbox(label, key=f"g_{key}")

        st.markdown("---")

        # --- TIPOS DE EXHIBIDORES ---
        st.markdown("### 🏪 Tipos de Exhibidores")
        tipos = {
            "LEGOS_GC": "LEGOS G&C",
            "TOBOGAN_RITZ_OREO": "TOBOGÁN (Ritz/Oreo)",
            "EXHIB_KIWI": "EXHIB KIWI"
        }
        cols3 = st.columns(3)
        tipos_vals = {}
        for i, (key, label) in enumerate(tipos.items()):
            with cols3[i]:
                tipos_vals[key] = st.checkbox(label, key=f"t_{key}")

        st.markdown("---")

        # --- CONTAMINACIÓN ---
        st.markdown("### ⚠️ Contaminación de Exhibidores")
        st.markdown('<div class="leyenda-box">Marca los exhibidores que presentan contaminación con productos de terceros</div>', unsafe_allow_html=True)
        cont = {
            "CONT_LEGOS_GC": "LEGOS G&C",
            "CONT_TOBOGAN_RITZ_OREO": "TOBOGÁN (Ritz/Oreo)",
            "CONT_EXHIB_KIWI": "EXHIB KIWI"
        }
        cols_cont = st.columns(3)
        cont_vals = {}
        for i, (key, label) in enumerate(cont.items()):
            with cols_cont[i]:
                cont_vals[key] = st.checkbox(label, key=f"c_{key}")

        st.markdown("---")

        # --- EXHIBIDORES POP ---
        st.markdown("### 🎯 Exhibidores POP / Ubicación")
        exhib = {
            "Esb_Legos": "Esb. Legos",
            "Esb_Tobogan": "Esb. Tobogán",
            "Esb_Kiwi": "Esb. Kiwi",
            "ExhibPOP_Oport": "Exhib POP Oportunidad",
            "ExhibPOP_Kiwi_Oport": "Exhib POP Kiwi Oport.",
            "Ubicacion_Preferencial": "Ubicación Preferencial"
        }
        cols4 = st.columns(3)
        exhib_vals = {}
        for i, (key, label) in enumerate(exhib.items()):
            with cols4[i % 3]:
                exhib_vals[key] = st.checkbox(label, key=f"e_{key}")

        st.markdown("---")

        # --- VISIBILIDAD ---
        st.markdown("### 👁️ Visibilidad")
        st.markdown('<div class="leyenda-box">1 = Alta Visibilidad &nbsp;&nbsp;|&nbsp;&nbsp; 2 = Visibilidad Media &nbsp;&nbsp;|&nbsp;&nbsp; 3 = Baja Visibilidad</div>', unsafe_allow_html=True)
        visibilidad = st.radio(
            "Nivel de visibilidad",
            options=[1, 2, 3],
            format_func=lambda x: {1: "1 - Alta Visibilidad", 2: "2 - Visibilidad Media", 3: "3 - Baja Visibilidad"}[x],
            horizontal=True
        )

        st.markdown("---")

        # --- COLOCACIÓN TERCEROS ---
        st.markdown("### 🏷️ Colocación de Terceros")
        col_terc1, col_terc2 = st.columns([1, 2])
        with col_terc1:
            colocacion_terceros = st.radio("¿Hay colocación de terceros?", options=["No", "Sí"], horizontal=True)
        with col_terc2:
            marca_tercero = st.text_input("Marca del tercero (si aplica)", placeholder="Ej: Gloria, Alicorp...")

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
            if not codigo_pdc or not nombre_cliente or giro_negocio == "Selecciona...":
                st.error("Por favor completa el Código PDC, Nombre del Cliente y Giro de Negocio.")
            else:
                registro = {
                    "Fecha": str(fecha),
                    "Codigo_PDC": codigo_pdc,
                    "Nombre_Cliente": nombre_cliente,
                    "Giro_Negocio": giro_negocio,
                    **{k: int(v) for k, v in biscuits_vals.items()},
                    **{k: int(v) for k, v in gyc_vals.items()},
                    **{k: int(v) for k, v in tipos_vals.items()},
                    **{k: int(v) for k, v in cont_vals.items()},
                    **{k: int(v) for k, v in exhib_vals.items()},
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

# ═══════════════════════════════════════════
# PÁGINA: DASHBOARD
# ═══════════════════════════════════════════
elif st.session_state.pagina == "dashboard":

    df = cargar_datos()

    col_title, col_btn = st.columns([5, 1])
    with col_title:
        st.markdown("# 📊 Dashboard - Supervisión Canal Tradicional")
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

    total_visitas = len(df)
    total_ventas = df["Efectividad"].sum()
    ticket_prom = df["Ticket_Promedio"].mean()
    tiempo_prom = df["Tiempo_PDC"].mean()

    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-box"><div class="kpi-label">Total visitas</div>
            <div class="kpi-value">{total_visitas}</div><div class="kpi-sub">registros</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-box"><div class="kpi-label">Total ventas</div>
            <div class="kpi-value">{int(total_ventas)}</div><div class="kpi-sub">efectividad acumulada</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-box"><div class="kpi-label">Ticket promedio</div>
            <div class="kpi-value">S/ {ticket_prom:.2f}</div><div class="kpi-sub">promedio por visita</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-box"><div class="kpi-label">Tiempo en PDC</div>
            <div class="kpi-value">{tiempo_prom:.0f} min</div><div class="kpi-sub">promedio por visita</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("#### Efectividad por fecha")
        df_fecha = df.groupby("Fecha")["Efectividad"].sum().reset_index()
        fig1 = px.bar(df_fecha, x="Fecha", y="Efectividad", color_discrete_sequence=["#1a1a1a"])
        fig1.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_family="DM Sans", margin=dict(t=20, b=20))
        st.plotly_chart(fig1, use_container_width=True)

    with col_g2:
        st.markdown("#### Visitas por giro de negocio")
        if "Giro_Negocio" in df.columns:
            df_giro = df["Giro_Negocio"].value_counts().reset_index()
            df_giro.columns = ["Giro", "Visitas"]
            fig_giro = px.pie(df_giro, names="Giro", values="Visitas", color_discrete_sequence=px.colors.sequential.Greys_r)
            fig_giro.update_layout(paper_bgcolor="white", font_family="DM Sans", margin=dict(t=20, b=20))
            st.plotly_chart(fig_giro, use_container_width=True)

    col_g3, col_g4 = st.columns(2)
    with col_g3:
        st.markdown("#### Visibilidad promedio por fecha")
        if "Visibilidad" in df.columns:
            df["Visibilidad"] = pd.to_numeric(df["Visibilidad"], errors="coerce")
            df_vis = df.groupby("Fecha")["Visibilidad"].mean().reset_index()
            fig_vis = px.line(df_vis, x="Fecha", y="Visibilidad", markers=True, color_discrete_sequence=["#555"])
            fig_vis.update_yaxes(range=[0.5, 3.5], tickvals=[1, 2, 3], ticktext=["1 - Alta", "2 - Media", "3 - Baja"])
            fig_vis.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_family="DM Sans", margin=dict(t=20, b=20))
            st.plotly_chart(fig_vis, use_container_width=True)

    with col_g4:
        st.markdown("#### Colocación de terceros")
        if "Colocacion_Terceros" in df.columns:
            df_terc = df["Colocacion_Terceros"].value_counts().reset_index()
            df_terc.columns = ["Respuesta", "Cantidad"]
            fig_terc = px.bar(df_terc, x="Respuesta", y="Cantidad", color_discrete_sequence=["#1a1a1a", "#aaa"])
            fig_terc.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_family="DM Sans", margin=dict(t=20, b=20))
            st.plotly_chart(fig_terc, use_container_width=True)

    st.markdown("#### Presencia de productos (% de visitas)")
    productos = [
        "OREO_34GR", "OREO_54GR", "OREO_ROLLO", "RITZ_ROLLO", "RITZ_TACO",
        "FIELD_CC", "FIELD_DP", "FIELD_VAIN", "TRIDENT_5s", "HALLS_12s", "CHICLETS_2S"
    ]
    presencia_pct = []
    for p in productos:
        if p in df.columns:
            pct = pd.to_numeric(df[p], errors="coerce").mean() * 100
            presencia_pct.append({"Producto": p.replace("_", " "), "Presencia %": round(pct, 1)})

    df_pres = pd.DataFrame(presencia_pct).sort_values("Presencia %", ascending=True)
    fig3 = px.bar(df_pres, x="Presencia %", y="Producto", orientation="h",
                  color="Presencia %", color_continuous_scale=["#e8e6e0", "#1a1a1a"], range_x=[0, 100])
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_family="DM Sans",
                       margin=dict(t=10, b=20), coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### Últimas visitas")
    cols_tabla = ["Fecha", "Codigo_PDC", "Nombre_Cliente", "Giro_Negocio", "Efectividad", "Ticket_Promedio", "Tiempo_PDC", "Visibilidad", "Colocacion_Terceros", "Marca_Tercero"]
    cols_existentes = [c for c in cols_tabla if c in df.columns]
    st.dataframe(
        df[cols_existentes].sort_values("Fecha", ascending=False).head(20).reset_index(drop=True),
        use_container_width=True
    )
