import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import os
import io
import base64
import zipfile

st.set_page_config(page_title="SUPERVISIÓN CANAL TRADICIONAL", layout="wide", page_icon=None)

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
    .btn-danger > button { background: #e05252 !important; color: white !important; border: none !important; }
    .btn-danger > button:hover { background: #c0392b !important; }
</style>
""", unsafe_allow_html=True)

CSV_FILE = "visitas.csv"
IMG_FOLDER = "imagenes_visita"
os.makedirs(IMG_FOLDER, exist_ok=True)

# Ticket_Promedio se elimina del formulario; se calcula en el dashboard
COLUMNAS = [
    "Fecha", "Codigo_PDC", "Nombre_Cliente", "Giro_Negocio",
    "Vendedor", "Codigo_Vendedor", "Mesa", "Zona", "Latitud", "Longitud",
    "OREO_34GR", "OREO_54GR", "OREO_ROLLO", "RITZ_ROLLO", "RITZ_TACO",
    "FIELD_CC", "FIELD_DP", "FIELD_VAIN", "CLUB_SOCIAL_TRA", "CLUB_SOCIAL_SAB",
    "TRIDENT_5s", "TRIDENT_EVUP", "HALLS_12s", "HALLS_100s", "CHICLETS_2S",
    "LEGOS_GC", "TOBOGAN_RITZ_OREO", "EXHIB_KIWI",
    "CONT_LEGOS_GC", "CONT_TOBOGAN_RITZ_OREO", "CONT_EXHIB_KIWI", "Causa_Contaminacion",
    "Visibilidad_Legos", "Visibilidad_Tobogan", "Visibilidad_Kiwi",
    "Colocacion_Terceros", "Marca_Tercero",
    "Efectividad_Soles", "Tiempo_PDC",
    "Imagen_Path"
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

def eliminar_historial():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    # También eliminar imágenes si existen
    if os.path.exists(IMG_FOLDER):
        for f in os.listdir(IMG_FOLDER):
            os.remove(os.path.join(IMG_FOLDER, f))

if "pagina" not in st.session_state:
    st.session_state.pagina = "formulario"
if "confirmar_eliminar" not in st.session_state:
    st.session_state.confirmar_eliminar = False
if "gps_lat" not in st.session_state:
    st.session_state.gps_lat = ""
if "gps_lon" not in st.session_state:
    st.session_state.gps_lon = ""

# ═══════════════════════════════════════════
# PÁGINA: FORMULARIO
# ═══════════════════════════════════════════
if st.session_state.pagina == "formulario":

    df_check = cargar_datos()
    if not df_check.empty:
        col_nav1, col_nav2 = st.columns([6, 1])
        with col_nav2:
            if st.button("Ver Dashboard"):
                st.session_state.pagina = "dashboard"
                st.rerun()

    st.markdown("# Registro de Visita")
    st.markdown("---")

    # ─── UBICACIÓN DEL PDC ────────────────────────────────────────────────
    import requests as _req
    st.markdown("### Ubicación del PDC")

    # ── Si ya hay coords guardadas ─────────────────────────────────────────
    if st.session_state.gps_lat and st.session_state.gps_lon:
        st.success(f"✅ Ubicación guardada: **{st.session_state.gps_lat}, {st.session_state.gps_lon}**")
        if st.button("Cambiar ubicación"):
            st.session_state.gps_lat = ""
            st.session_state.gps_lon = ""
            if "geo_resultados" in st.session_state:
                del st.session_state["geo_resultados"]
            st.rerun()
    else:
        # ── Buscar por dirección (siempre disponible) ─────────────────────
        st.caption("O busca la dirección del PDC:")
        col_dir1, col_dir2 = st.columns([4, 1])
        with col_dir1:
            dir_input = st.text_input(
                "Dirección",
                placeholder="Ej: Av. España 1234, Trujillo, Peru",
                label_visibility="collapsed",
                key="dir_input"
            )
        with col_dir2:
            buscar = st.button("Buscar", use_container_width=True, key="btn_buscar_dir")

        if buscar and dir_input.strip():
            try:
                r = _req.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": dir_input.strip(), "format": "json", "limit": 5, "countrycodes": "pe"},
                    headers={"User-Agent": "MDZ-SupervisionApp/1.0"},
                    timeout=8
                )
                res = r.json()
                if res:
                    st.session_state["geo_resultados"] = res
                else:
                    st.warning("Sin resultados. Prueba con más detalle, ej: 'Av. España 123, Trujillo, La Libertad, Peru'")
            except Exception as ex:
                st.error(f"Error de conexión: {ex}")

        if st.session_state.get("geo_resultados"):
            res = st.session_state["geo_resultados"]
            opts = {r["display_name"][:90]: (r["lat"], r["lon"]) for r in res}
            elegida = st.selectbox("Selecciona la ubicación:", list(opts.keys()), key="geo_sel")
            if st.button("Confirmar esta ubicación", key="geo_ok"):
                la, lo = opts[elegida]
                st.session_state.gps_lat = str(round(float(la), 6))
                st.session_state.gps_lon = str(round(float(lo), 6))
                del st.session_state["geo_resultados"]
                st.rerun()

        # ── OPCIÓN 3: Coordenadas manuales ─────────────────────────────────
        with st.expander("Ingresar coordenadas manualmente"):
            cm1, cm2, cm3 = st.columns([2, 2, 1])
            with cm1:
                lat_m = st.text_input("Latitud", placeholder="-8.111640", key="lat_man")
            with cm2:
                lon_m = st.text_input("Longitud", placeholder="-79.028700", key="lon_man")
            with cm3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Guardar", key="btn_manual"):
                    if lat_m and lon_m:
                        st.session_state.gps_lat = lat_m.strip()
                        st.session_state.gps_lon = lon_m.strip()
                        st.rerun()

    st.markdown("---")

    with st.form("form_visita", clear_on_submit=False):

        # ─── SECCIÓN: DATOS DEL CLIENTE ───────────────────────────────────
        st.markdown("### Datos del Cliente")
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha = st.date_input("Fecha de Visita", value=date.today())
        with col2:
            codigo_pdc = st.text_input("Código PDC (8 dígitos)", max_chars=8, placeholder="Ej: 00000001")
        with col3:
            nombre_cliente = st.text_input("Nombre del Cliente", placeholder="Ej: Bodega Central")

        col4, col5 = st.columns(2)
        with col4:
            giro_negocio = st.selectbox("Giro de Negocio", [
                "Selecciona...",
                "1 - Bodega",
                "2 - Minimarket / Tiendas",
                "3 - Kiosko",
                "4 - Especializados (Panificadora, Horeca, Internet...)",
                "5 - Otros (Puesto de mercado, Centros Educativos...)"
            ])
        with col5:
            zona = st.text_input("Zona", placeholder="Ej: Norte, Centro, Sur...")

        # coords desde session_state (capturadas por búsqueda de dirección)
        latitud  = st.session_state.gps_lat
        longitud = st.session_state.gps_lon

        st.markdown("---")

        # ─── SECCIÓN: DATOS DEL VENDEDOR ──────────────────────────────────
        st.markdown("### Datos del Vendedor")
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            vendedor = st.text_input("Nombre del Vendedor", placeholder="Nombre del vendedor")
        with col_v2:
            codigo_vendedor = st.text_input("Código de Vendedor", placeholder="Ej: VEN001")
        with col_v3:
            mesa = st.text_input("Mesa", placeholder="Ej: Mesa 1, Mesa Norte...")

        st.markdown("---")

        # ─── PRESENCIA BISCUITS ───────────────────────────────────────────
        st.markdown("### Presencia Biscuits")
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

        # ─── PRESENCIA G&C ────────────────────────────────────────────────
        st.markdown("### Presencia G&C")
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

        # ─── TIPOS DE EXHIBIDORES ─────────────────────────────────────────
        st.markdown("### Tipos de Exhibidores")
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

        # ─── CONTAMINACIÓN ────────────────────────────────────────────────
        st.markdown("### Contaminación de Exhibidores")
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
        causa_contaminacion = st.text_input(
            "Identifique las causas de contaminación (si aplica)",
            placeholder="Ej: Productos Gloria en exhibidor Legos..."
        )

        st.markdown("---")

        # ─── VISIBILIDAD ──────────────────────────────────────────────────
        st.markdown("### Visibilidad por Exhibidor")
        st.markdown(
            '<div class="leyenda-box">0 = No Tiene &nbsp;&nbsp;|&nbsp;&nbsp; '
            '1 = Alta Visibilidad &nbsp;&nbsp;|&nbsp;&nbsp; 2 = Visibilidad Media &nbsp;&nbsp;|&nbsp;&nbsp; '
            '3 = Baja Visibilidad</div>',
            unsafe_allow_html=True
        )
        VIS_OPTIONS = [0, 1, 2, 3]
        VIS_LABELS = {0: "0 - No Tiene", 1: "1 - Alta", 2: "2 - Media", 3: "3 - Baja"}
        v1, v2, v3 = st.columns(3)
        with v1:
            vis_legos = st.radio("LEGOS G&C", options=VIS_OPTIONS,
                format_func=lambda x: VIS_LABELS[x], horizontal=True, key="vl")
        with v2:
            vis_tobogan = st.radio("TOBOGÁN (Ritz/Oreo)", options=VIS_OPTIONS,
                format_func=lambda x: VIS_LABELS[x], horizontal=True, key="vt")
        with v3:
            vis_kiwi = st.radio("EXHIB KIWI", options=VIS_OPTIONS,
                format_func=lambda x: VIS_LABELS[x], horizontal=True, key="vk")

        st.markdown("---")

        # ─── COLOCACIÓN TERCEROS ──────────────────────────────────────────
        st.markdown("### Colocación de Terceros")
        col_terc1, col_terc2 = st.columns([1, 3])
        with col_terc1:
            colocacion_terceros = st.radio("¿Hay colocación de terceros?", options=["No", "Sí"], horizontal=True)
        with col_terc2:
            t1, t2, t3, t4 = st.columns(4)
            with t1:
                marca_tercero_1 = st.text_input("Marca 1", placeholder="Ej: Gloria", key="mt1")
            with t2:
                marca_tercero_2 = st.text_input("Marca 2", placeholder="Ej: Alicorp", key="mt2")
            with t3:
                marca_tercero_3 = st.text_input("Marca 3", placeholder="Ej: Laive", key="mt3")
            with t4:
                marca_tercero_4 = st.text_input("Marca 4", placeholder="Ej: Nestlé", key="mt4")
        marca_tercero = ", ".join([m for m in [marca_tercero_1, marca_tercero_2, marca_tercero_3, marca_tercero_4] if m.strip()])

        st.markdown("---")

        # ─── KPIs NUMÉRICOS (sin Ticket Promedio) ─────────────────────────
        st.markdown("### Indicadores de la visita")
        k1, k2 = st.columns(2)
        with k1:
            efectividad_soles = st.number_input(
                "Efectividad (S/)", min_value=0.0, step=1.0, value=0.0, format="%.2f"
            )
        with k2:
            tiempo_pdc = st.number_input(
                "Tiempo en PDC (minutos)", min_value=0, step=1, value=0
            )

        st.markdown("---")

        # ─── IMAGEN ───────────────────────────────────────────────────────
        st.markdown("### Evidencia fotográfica")
        imagen_subida = st.file_uploader("Sube una imagen de la visita (JPG, PNG)", type=["jpg", "jpeg", "png"])

        st.markdown("---")

        submitted = st.form_submit_button("Guardar y ver dashboard", use_container_width=True)

        if submitted:
            if not codigo_pdc or not nombre_cliente or giro_negocio == "Selecciona...":
                st.error("Por favor completa el Código PDC, Nombre del Cliente y Giro de Negocio.")
            else:
                img_path = ""
                if imagen_subida is not None:
                    img_filename = f"{codigo_pdc}_{str(fecha)}_{imagen_subida.name}"
                    img_path = os.path.join(IMG_FOLDER, img_filename)
                    with open(img_path, "wb") as f:
                        f.write(imagen_subida.getbuffer())

                registro = {
                    "Fecha": str(fecha),
                    "Codigo_PDC": codigo_pdc,
                    "Nombre_Cliente": nombre_cliente,
                    "Giro_Negocio": giro_negocio,
                    "Vendedor": vendedor,
                    "Codigo_Vendedor": codigo_vendedor,
                    "Mesa": mesa,
                    "Zona": zona,
                    "Latitud": latitud,
                    "Longitud": longitud,
                    **{k: int(v) for k, v in biscuits_vals.items()},
                    **{k: int(v) for k, v in gyc_vals.items()},
                    **{k: int(v) for k, v in tipos_vals.items()},
                    **{k: int(v) for k, v in cont_vals.items()},
                    "Causa_Contaminacion": causa_contaminacion,
                    "Visibilidad_Legos": vis_legos,
                    "Visibilidad_Tobogan": vis_tobogan,
                    "Visibilidad_Kiwi": vis_kiwi,
                    "Colocacion_Terceros": colocacion_terceros,
                    "Marca_Tercero": marca_tercero,
                    "Efectividad_Soles": efectividad_soles,
                    "Tiempo_PDC": tiempo_pdc,
                    "Imagen_Path": img_path
                }
                guardar_registro(registro)
                st.session_state.pagina = "dashboard"
                st.rerun()


# ═══════════════════════════════════════════
# PÁGINA: DASHBOARD
# ═══════════════════════════════════════════
elif st.session_state.pagina == "dashboard":

    df = cargar_datos()

    # ── BARRA SUPERIOR ────────────────────────────────────────────────────
    col_title, col_btn1, col_btn2, col_btn3 = st.columns([4, 1, 1, 1])
    with col_title:
        st.markdown("# Dashboard - Supervisión Canal Tradicional")
    with col_btn1:
        if st.button("Ingresar datos"):
            st.session_state.pagina = "formulario"
            st.rerun()
    with col_btn2:
        if st.button("Nueva visita"):
            st.session_state.pagina = "formulario"
            st.rerun()
    with col_btn3:
        # Botón de eliminar historial con confirmación
        if not st.session_state.confirmar_eliminar:
            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
            if st.button("Eliminar historial"):
                st.session_state.confirmar_eliminar = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("¿Seguro? Esta acción no se puede deshacer.")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("Sí, eliminar todo"):
                    eliminar_historial()
                    st.session_state.confirmar_eliminar = False
                    st.session_state.pagina = "formulario"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                if st.button("Cancelar"):
                    st.session_state.confirmar_eliminar = False
                    st.rerun()

    if df.empty:
        st.warning("No hay registros aún.")
        st.stop()

    df["Fecha"] = pd.to_datetime(df["Fecha"])
    for col in ["Efectividad_Soles", "Tiempo_PDC"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    st.markdown("---")

    # ── FILTRO DE FECHAS ──────────────────────────────────────────────────
    st.markdown("#### Filtrar por rango de fechas")
    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()

    col_f1, col_f2, col_f3 = st.columns([2, 2, 3])
    with col_f1:
        fecha_desde = st.date_input("Desde", value=fecha_min, min_value=fecha_min, max_value=fecha_max, key="fd")
    with col_f2:
        fecha_hasta = st.date_input("Hasta", value=fecha_max, min_value=fecha_min, max_value=fecha_max, key="fh")
    with col_f3:
        vendedores_disponibles = ["Todos"] + sorted(df["Vendedor"].dropna().unique().tolist())
        filtro_vendedor = st.selectbox("Filtrar por Vendedor", vendedores_disponibles)

    # Aplicar filtros
    mask = (df["Fecha"].dt.date >= fecha_desde) & (df["Fecha"].dt.date <= fecha_hasta)
    df_f = df[mask].copy()
    if filtro_vendedor != "Todos":
        df_f = df_f[df_f["Vendedor"] == filtro_vendedor]

    if df_f.empty:
        st.warning("No hay registros en el rango de fechas seleccionado.")
        st.stop()

    # ── TICKET PROMEDIO CALCULADO ─────────────────────────────────────────
    # Por vendedor y fecha: ventas totales del vendedor ÷ clientes únicos visitados ese día
    df_f["Fecha_str"] = df_f["Fecha"].dt.date.astype(str)
    ticket_calc = (
        df_f.groupby(["Vendedor", "Fecha_str"])
        .agg(
            Ventas_Dia=("Efectividad_Soles", "sum"),
            Clientes_Dia=("Codigo_PDC", "nunique")
        )
        .reset_index()
    )
    ticket_calc["Ticket_Calculado"] = ticket_calc.apply(
        lambda r: r["Ventas_Dia"] / r["Clientes_Dia"] if r["Clientes_Dia"] > 0 else 0, axis=1
    )
    ticket_prom_global = ticket_calc["Ticket_Calculado"].mean() if not ticket_calc.empty else 0

    # ── KPIs ──────────────────────────────────────────────────────────────
    total_visitas = len(df_f)
    total_ventas = df_f["Efectividad_Soles"].sum()
    tiempo_prom = df_f["Tiempo_PDC"].mean()
    pct_con_terceros = (df_f["Colocacion_Terceros"] == "Sí").mean() * 100 if "Colocacion_Terceros" in df_f.columns else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        (k1, "Total Visitas", f"{total_visitas}", "registros filtrados"),
        (k2, "Efectividad Total", f"S/ {total_ventas:,.2f}", "ventas acumuladas"),
        (k3, "Ticket Promedio", f"S/ {ticket_prom_global:.2f}", "ventas ÷ clientes / día / vendedor"),
        (k4, "Tiempo en PDC", f"{tiempo_prom:.0f} min", "promedio por visita"),
        (k5, "Colocación Terceros", f"{pct_con_terceros:.0f}%", "de visitas con terceros"),
    ]
    for col, label, value, sub in kpis:
        with col:
            st.markdown(f"""<div class="kpi-box"><div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>""",
                unsafe_allow_html=True)

    st.markdown("---")

    # ── TICKET PROMEDIO POR VENDEDOR (tabla detallada) ────────────────────
    st.markdown("#### Ticket Promedio por Vendedor y Día")
    st.caption("Ventas totales del vendedor ÷ clientes únicos visitados ese día")
    ticket_display = ticket_calc.rename(columns={
        "Vendedor": "Vendedor",
        "Fecha_str": "Fecha",
        "Ventas_Dia": "Ventas del Día (S/)",
        "Clientes_Dia": "Clientes Visitados",
        "Ticket_Calculado": "Ticket Promedio (S/)"
    })
    ticket_display["Ventas del Día (S/)"] = ticket_display["Ventas del Día (S/)"].map("S/ {:,.2f}".format)
    ticket_display["Ticket Promedio (S/)"] = ticket_display["Ticket Promedio (S/)"].map("S/ {:,.2f}".format)
    st.dataframe(ticket_display, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── FILA 1: Colocación Exhibidores + Giros de Negocio + Colocación Terceros ──
    col_g1, col_g2, col_g3 = st.columns(3)

    with col_g1:
        st.markdown("#### Colocación Exhibidores")
        exhib_cols = {
            "LEGOS_GC": "LEGOS (G&C)",
            "TOBOGAN_RITZ_OREO": "TOBOGÁN (Ritz/Oreo)",
            "EXHIB_KIWI": "EXHIB KIWI"
        }
        data_exhib = []
        for col_name, label in exhib_cols.items():
            if col_name in df_f.columns:
                data_exhib.append({
                    "Exhibidor": label,
                    "Cantidad": int(pd.to_numeric(df_f[col_name], errors="coerce").fillna(0).sum())
                })
        sin_exhib = int(
            (df_f[list(exhib_cols.keys())].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1) == 0).sum()
        ) if all(c in df_f.columns for c in exhib_cols) else 0
        data_exhib.append({"Exhibidor": "SIN EXHIBIDORES", "Cantidad": sin_exhib})
        df_exhib = pd.DataFrame(data_exhib)
        fig_exhib = px.bar(df_exhib, x="Exhibidor", y="Cantidad", text="Cantidad",
                           color="Exhibidor",
                           color_discrete_sequence=["#6a9e4f", "#e05252", "#7b5ea7", "#b0b0b0"])
        fig_exhib.update_traces(textposition="outside")
        fig_exhib.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
                                font_family="DM Sans", margin=dict(t=20, b=20),
                                xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_exhib, use_container_width=True)

    with col_g2:
        st.markdown("#### Giros de Negocio")
        if "Giro_Negocio" in df_f.columns:
            df_giro = df_f["Giro_Negocio"].value_counts().reset_index()
            df_giro.columns = ["Giro", "Visitas"]
            df_giro["Giro"] = df_giro["Giro"].str.replace(r"^\d+ - ", "", regex=True)
            fig_giro = px.pie(df_giro, names="Giro", values="Visitas",
                              color_discrete_sequence=["#4472C4", "#FF7F0E", "#7f7f7f", "#FFBF00", "#2196F3"])
            fig_giro.update_traces(textinfo="label+value")
            fig_giro.update_layout(paper_bgcolor="white", font_family="DM Sans", margin=dict(t=20, b=20))
            st.plotly_chart(fig_giro, use_container_width=True)

    with col_g3:
        st.markdown("#### Colocación de Terceros")
        if "Colocacion_Terceros" in df_f.columns:
            df_terc_sino = df_f["Colocacion_Terceros"].value_counts().reset_index()
            df_terc_sino.columns = ["Estado", "Cantidad"]
            fig_terc = px.pie(
                df_terc_sino, names="Estado", values="Cantidad",
                hole=0.45,
                color="Estado",
                color_discrete_map={"Sí": "#e05252", "No": "#6a9e4f"}
            )
            fig_terc.update_traces(textinfo="label+percent")
            fig_terc.update_layout(paper_bgcolor="white", font_family="DM Sans",
                                   margin=dict(t=20, b=5), legend_title_text="")
            st.plotly_chart(fig_terc, use_container_width=True)
            if "Marca_Tercero" in df_f.columns:
                df_marcas = df_f[
                    (df_f["Colocacion_Terceros"] == "Sí") &
                    (df_f["Marca_Tercero"].notna()) &
                    (df_f["Marca_Tercero"].str.strip() != "")
                ]["Marca_Tercero"].str.strip().str.upper().value_counts().reset_index()
                df_marcas.columns = ["Marca", "Visitas"]
                if not df_marcas.empty:
                    st.caption("Marcas de terceros detectadas")
                    fig_marcas = px.bar(
                        df_marcas, x="Visitas", y="Marca", orientation="h",
                        text="Visitas", color_discrete_sequence=["#e05252"]
                    )
                    fig_marcas.update_traces(textposition="outside")
                    fig_marcas.update_layout(
                        plot_bgcolor="white", paper_bgcolor="white",
                        font_family="DM Sans", margin=dict(t=5, b=5),
                        xaxis_title="", yaxis_title=""
                    )
                    st.plotly_chart(fig_marcas, use_container_width=True)

    st.markdown("---")

    # ── FILA 2: Efectividad + Mapa ─────────────────────────────────────────
    col_g4, col_g5 = st.columns(2)

    with col_g4:
        st.markdown("#### Efectividad")
        df_f["Concreto"] = df_f["Efectividad_Soles"].apply(
            lambda x: "CONCRETO VENTA" if x > 0 else "NO CONCRETO VENTA"
        )
        df_efec = df_f["Concreto"].value_counts().reset_index()
        df_efec.columns = ["Estado", "Cantidad"]
        df_efec["Pct"] = (
            (df_efec["Cantidad"] / df_efec["Cantidad"].sum() * 100).round(0).astype(int).astype(str) + "%"
        )
        fig_efec = px.bar(df_efec, y="Estado", x="Cantidad", orientation="h", text="Pct",
                          color="Estado",
                          color_discrete_map={
                              "CONCRETO VENTA": "#7b5ea7",
                              "NO CONCRETO VENTA": "#e05252"
                          })
        fig_efec.update_traces(textposition="outside")
        fig_efec.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
                               font_family="DM Sans", margin=dict(t=20, b=20),
                               xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_efec, use_container_width=True)

    with col_g5:
        st.markdown("#### Mapa de visitas")
        if "Latitud" in df_f.columns and "Longitud" in df_f.columns:
            df_map = df_f.copy()
            df_map["Latitud"] = pd.to_numeric(df_map["Latitud"], errors="coerce")
            df_map["Longitud"] = pd.to_numeric(df_map["Longitud"], errors="coerce")
            df_map = df_map.dropna(subset=["Latitud", "Longitud"])
            if not df_map.empty:
                fig_map = px.scatter_mapbox(
                    df_map, lat="Latitud", lon="Longitud",
                    hover_name="Nombre_Cliente",
                    hover_data={"Zona": True, "Efectividad_Soles": True, "Giro_Negocio": True},
                    color="Zona" if "Zona" in df_map.columns else None,
                    zoom=14, height=350
                )
                fig_map.update_layout(mapbox_style="open-street-map",
                                      margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.info("Agrega visitas con latitud y longitud para ver el mapa.")

    st.markdown("---")

    # ── PRESENCIA DE PRODUCTOS ────────────────────────────────────────────
    st.markdown("#### Presencia de productos (% de visitas)")
    productos = {
        "OREO_34GR": "OREO 34GR", "OREO_54GR": "OREO 54GR", "OREO_ROLLO": "OREO ROLLO",
        "RITZ_ROLLO": "RITZ ROLLO", "RITZ_TACO": "RITZ TACO",
        "FIELD_CC": "FIELD CC", "FIELD_DP": "FIELD DP", "FIELD_VAIN": "FIELD VAIN",
        "TRIDENT_5s": "TRIDENT 5s", "HALLS_12s": "HALLS 12s", "CHICLETS_2S": "CHICLETS 2S"
    }
    presencia_pct = []
    for key, label in productos.items():
        if key in df_f.columns:
            pct = pd.to_numeric(df_f[key], errors="coerce").mean() * 100
            presencia_pct.append({"Producto": label, "Presencia %": round(pct, 1)})
    df_pres = pd.DataFrame(presencia_pct).sort_values("Presencia %", ascending=True)
    fig_pres = px.bar(df_pres, x="Presencia %", y="Producto", orientation="h",
                      color="Presencia %",
                      color_continuous_scale=["#e8e6e0", "#7b5ea7"],
                      range_x=[0, 100], text="Presencia %")
    fig_pres.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_pres.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_family="DM Sans",
                           margin=dict(t=10, b=20), coloraxis_showscale=False)
    st.plotly_chart(fig_pres, use_container_width=True)

    st.markdown("---")

    # ── TABLA ÚLTIMAS VISITAS ─────────────────────────────────────────────
    st.markdown("#### Últimas visitas")
    cols_tabla = [
        "Fecha", "Codigo_PDC", "Nombre_Cliente", "Giro_Negocio",
        "Vendedor", "Codigo_Vendedor", "Mesa", "Zona",
        "Efectividad_Soles", "Tiempo_PDC",
        "Visibilidad_Legos", "Visibilidad_Tobogan", "Visibilidad_Kiwi",
        "Colocacion_Terceros", "Marca_Tercero"
    ]
    cols_existentes = [c for c in cols_tabla if c in df_f.columns]
    df_tabla = df_f[cols_existentes].sort_values("Fecha", ascending=False).head(50).reset_index(drop=True)
    st.dataframe(df_tabla, use_container_width=True)

    st.markdown("---")

    # ── DESCARGAS ─────────────────────────────────────────────────────────
    st.markdown("#### Descargas")
    dcol1, dcol2 = st.columns(2)

    with dcol1:
        buffer = io.BytesIO()
        export_df = df_f.copy()
        # Añadir ticket calculado al export
        export_df = export_df.merge(
            ticket_calc[["Vendedor", "Fecha_str", "Ticket_Calculado"]],
            left_on=["Vendedor", "Fecha_str"], right_on=["Vendedor", "Fecha_str"], how="left"
        )
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            export_df.drop(columns=["Imagen_Path", "Fecha_str", "Concreto", "Giro_Corto"],
                           errors="ignore").to_excel(writer, index=False, sheet_name="Visitas")
        buffer.seek(0)
        st.download_button(
            label="Descargar datos en Excel",
            data=buffer,
            file_name=f"visitas_MDZ_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with dcol2:
        imagenes = []
        if "Imagen_Path" in df_f.columns:
            imagenes = [p for p in df_f["Imagen_Path"].dropna().tolist() if p and os.path.exists(str(p))]
        if imagenes:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for img_path in imagenes:
                    zf.write(img_path, os.path.basename(img_path))
            zip_buffer.seek(0)
            st.download_button(
                label=f"Descargar imágenes ({len(imagenes)} fotos)",
                data=zip_buffer,
                file_name=f"imagenes_MDZ_{date.today()}.zip",
                mime="application/zip",
                use_container_width=True
            )
        else:
            st.info("No hay imágenes guardadas aún.")
