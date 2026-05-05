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
    if os.path.exists(IMG_FOLDER):
        for f in os.listdir(IMG_FOLDER):
            os.remove(os.path.join(IMG_FOLDER, f))

# ── Session state defaults ─────────────────────────────────────────────────
if "pagina" not in st.session_state:
    st.session_state.pagina = "formulario"
if "confirmar_eliminar" not in st.session_state:
    st.session_state.confirmar_eliminar = False
if "gps_lat" not in st.session_state:
    st.session_state.gps_lat = ""
if "gps_lon" not in st.session_state:
    st.session_state.gps_lon = ""
if "snapshots" not in st.session_state:
    st.session_state.snapshots = {}

SNAPSHOTS_FILE = "snapshots.pkl"

def guardar_snapshots_disco():
    import pickle
    with open(SNAPSHOTS_FILE, "wb") as f:
        pickle.dump(st.session_state.snapshots, f)

def cargar_snapshots_disco():
    import pickle
    if os.path.exists(SNAPSHOTS_FILE):
        with open(SNAPSHOTS_FILE, "rb") as f:
            return pickle.load(f)
    return {}

# Cargar snapshots persistidos al iniciar
if not st.session_state.snapshots and os.path.exists(SNAPSHOTS_FILE):
    st.session_state.snapshots = cargar_snapshots_disco()

# ═══════════════════════════════════════════
# PÁGINA: FORMULARIO
# ═══════════════════════════════════════════
if st.session_state.pagina == "formulario":

    df_check = cargar_datos()
    if not df_check.empty:
        col_nav1, col_nav2 = st.columns([6, 1])
        with col_nav2:
            if st.button("📊 Ver Dashboard"):
                st.session_state.pagina = "dashboard"
                st.rerun()

    st.markdown("# Registro de Visita")
    st.markdown("---")

    # ─── UBICACIÓN DEL PDC ────────────────────────────────────────────────
    import requests as _req

    st.markdown("### 📍 Ubicación del PDC")

    if st.session_state.gps_lat and st.session_state.gps_lon:
        st.success(f"✅ Ubicación guardada: **{st.session_state.gps_lat}, {st.session_state.gps_lon}**")
        if st.button("Cambiar ubicación"):
            st.session_state.gps_lat = ""
            st.session_state.gps_lon = ""
            if "geo_resultados" in st.session_state:
                del st.session_state["geo_resultados"]
            st.rerun()
    else:
        # ── Buscar por dirección ──────────────────────────────────────────
        st.caption("Busca la dirección del PDC:")
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
            # Limpiar resultados anteriores
            if "geo_resultados" in st.session_state:
                del st.session_state["geo_resultados"]

            try:
                r = _req.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "q": dir_input.strip(),
                        "format": "json",
                        "limit": 5,
                        "countrycodes": "pe"
                    },
                    headers={"User-Agent": "MDZ-SupervisionApp/1.0"},
                    timeout=8
                )

                # ── CORRECCIÓN PRINCIPAL: validar respuesta antes de parsear ──
                if r.status_code != 200:
                    st.error(
                        f"El servicio de búsqueda devolvió un error (código {r.status_code}). "
                        "Intenta ingresando las coordenadas manualmente."
                    )
                elif not r.text.strip():
                    st.warning(
                        "El servicio de búsqueda no respondió. "
                        "Intenta ingresando las coordenadas manualmente."
                    )
                else:
                    try:
                        res = r.json()
                        if res:
                            st.session_state["geo_resultados"] = res
                        else:
                            st.warning(
                                "Sin resultados para esa dirección. "
                                "Prueba con más detalle, ej: "
                                "'Av. España 123, Trujillo, La Libertad, Peru'"
                            )
                    except ValueError:
                        st.error(
                            "La respuesta del servicio de búsqueda no es válida. "
                            "Intenta ingresando las coordenadas manualmente."
                        )

            except _req.exceptions.Timeout:
                st.error(
                    "La búsqueda tardó demasiado (timeout). "
                    "Verifica tu conexión o ingresa las coordenadas manualmente."
                )
            except _req.exceptions.ConnectionError:
                st.error(
                    "No se pudo conectar al servicio de búsqueda. "
                    "Ingresa las coordenadas manualmente."
                )
            except Exception as ex:
                st.error(
                    f"Error inesperado al buscar la dirección: {ex}. "
                    "Intenta ingresando las coordenadas manualmente."
                )

        # ── Mostrar resultados si existen ─────────────────────────────────
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

        # ── Coordenadas manuales ──────────────────────────────────────────
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
                        try:
                            float(lat_m.strip())
                            float(lon_m.strip())
                            st.session_state.gps_lat = lat_m.strip()
                            st.session_state.gps_lon = lon_m.strip()
                            st.rerun()
                        except ValueError:
                            st.error("Latitud y Longitud deben ser números. Ej: -8.111640")

    st.markdown("---")

    with st.form("form_visita", clear_on_submit=False):

        # ─── DATOS DEL CLIENTE ────────────────────────────────────────────
        st.markdown("### 🏪 Datos del Cliente")
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
            zona = st.selectbox("Zona", ["Selecciona...", "TRUJILLO", "VICTOR LARCO", "CALIFORNIA"])

        latitud  = st.session_state.gps_lat
        longitud = st.session_state.gps_lon

        st.markdown("---")

        # ─── DATOS DEL VENDEDOR ───────────────────────────────────────────
        st.markdown("### 🧑‍💼 Datos del Vendedor")
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            vendedor = st.text_input("Nombre del Vendedor", placeholder="Nombre del vendedor")
        with col_v2:
            codigo_vendedor = st.text_input("Código de Vendedor", max_chars=8, placeholder="Ej: VEN00001")
        with col_v3:
            mesa = st.selectbox("Mesa", ["Selecciona...", "DJ1", "DJ3"])

        ruta_logica = st.text_input("Ruta Lógica", placeholder="Ej: Ruta 01 - Norte")

        st.markdown("---")

        # ─── PRESENCIA BISCUITS ───────────────────────────────────────────
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

        # ─── PRESENCIA G&C ────────────────────────────────────────────────
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

        # ─── TIPOS DE EXHIBIDORES ─────────────────────────────────────────
        st.markdown("### 🗂️ Tipos de Exhibidores")
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
        st.markdown("### ⚠️ Contaminación de Exhibidores")
        cols_cont = st.columns(3)
        with cols_cont[0]:
            cont_legos = st.radio("LEGOS G&C", options=["No", "Sí"], horizontal=True, key="cr_legos")
        with cols_cont[1]:
            cont_tobogan = st.radio("TOBOGÁN (Ritz/Oreo)", options=["No", "Sí"], horizontal=True, key="cr_tobogan")
        with cols_cont[2]:
            cont_kiwi = st.radio("EXHIB KIWI", options=["No", "Sí"], horizontal=True, key="cr_kiwi")
        cont_vals = {
            "CONT_LEGOS_GC": 1 if cont_legos == "Sí" else 0,
            "CONT_TOBOGAN_RITZ_OREO": 1 if cont_tobogan == "Sí" else 0,
            "CONT_EXHIB_KIWI": 1 if cont_kiwi == "Sí" else 0,
        }

        st.markdown("---")

        # ─── VISIBILIDAD ──────────────────────────────────────────────────
        st.markdown("### 👁️ Visibilidad por Exhibidor")
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
        st.markdown("### 🏷️ Colocación de Terceros")
        col_terc1, col_terc2 = st.columns([1, 3])
        with col_terc1:
            colocacion_terceros = st.radio("¿Hay colocación de terceros?", options=["No", "Sí"], horizontal=True)
        with col_terc2:
            t1, t2, t3, t4 = st.columns(4)
            with t1:
                marca_tercero_1 = st.text_input("Marca 1", placeholder="Ej: Alicorp", key="mt1")
            with t2:
                marca_tercero_2 = st.text_input("Marca 2", placeholder="Ej: Molitalia", key="mt2")
            with t3:
                marca_tercero_3 = st.text_input("Marca 3", placeholder="Ej: Costa", key="mt3")
            with t4:
                marca_tercero_4 = st.text_input("Marca 4", placeholder="Ej: Nestlé", key="mt4")
        marca_tercero = ", ".join([m for m in [marca_tercero_1, marca_tercero_2, marca_tercero_3, marca_tercero_4] if m.strip()])

        st.markdown("---")

        # ─── KPIs NUMÉRICOS ───────────────────────────────────────────────
        st.markdown("### 📊 Indicadores de la visita")
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

        # ─── DETALLES IG ──────────────────────────────────────────────────
        st.markdown("### 📝 Detalles IG")
        detalles_ig = st.text_area(
            "Detalles IG",
            placeholder="Ingresa los detalles IG de la visita...",
            height=100,
            label_visibility="collapsed"
        )

        st.markdown("---")

        # ─── IMAGEN ───────────────────────────────────────────────────────
        st.markdown("### 📷 Evidencia fotográfica")
        imagen_subida = st.file_uploader("Sube una imagen de la visita (JPG, PNG)", type=["jpg", "jpeg", "png"])

        st.markdown("---")

        submitted = st.form_submit_button("💾 Guardar registro", use_container_width=True)

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

    col_title, col_btn1, col_btn2, col_btn3 = st.columns([4, 1, 1, 1])
    with col_title:
        st.markdown("# Dashboard — Supervisión Canal Tradicional")
    with col_btn1:
        if st.button("← Ingresar datos"):
            st.session_state.pagina = "formulario"
            st.rerun()
    with col_btn2:
        if st.button("＋ Nueva visita"):
            st.session_state.pagina = "formulario"
            st.rerun()
    with col_btn3:
        if not st.session_state.confirmar_eliminar:
            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
            if st.button("🗑 Eliminar historial"):
                st.session_state.confirmar_eliminar = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("¿Seguro? Esta acción no se puede deshacer.")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("Confirmar eliminación"):
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

    # ── FILTROS + HISTORIAL ───────────────────────────────────────────────
    st.markdown("#### 📅 Filtros y datos históricos")

    tab_actual, tab_historial = st.tabs(["📊 Datos actuales", "🗂️ Historial guardado"])

    with tab_actual:
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

        # ── GUARDAR SNAPSHOT ──────────────────────────────────────────────
        st.markdown("---")
        st.markdown("##### 💾 Guardar este período como histórico")
        sc1, sc2 = st.columns([3, 1])
        with sc1:
            nombre_snap = st.text_input(
                "Nombre del período",
                placeholder=f"Ej: Semana del {fecha_desde} al {fecha_hasta}",
                key="snap_nombre",
                label_visibility="collapsed"
            )
        with sc2:
            if st.button("💾 Guardar período", use_container_width=True, key="btn_guardar_snap"):
                mask_snap = (df["Fecha"].dt.date >= fecha_desde) & (df["Fecha"].dt.date <= fecha_hasta)
                df_snap = df[mask_snap].copy()
                if filtro_vendedor != "Todos":
                    df_snap = df_snap[df_snap["Vendedor"] == filtro_vendedor]
                if df_snap.empty:
                    st.warning("No hay datos en este rango para guardar.")
                else:
                    snap_key = nombre_snap.strip() if nombre_snap.strip() else f"{fecha_desde} → {fecha_hasta}"
                    if filtro_vendedor != "Todos":
                        snap_key += f" ({filtro_vendedor})"
                    st.session_state.snapshots[snap_key] = df_snap.to_csv(index=False)
                    guardar_snapshots_disco()
                    st.success(f"✅ Guardado como: **{snap_key}** ({len(df_snap)} registros)")

    with tab_historial:
        if not st.session_state.snapshots:
            st.info("Aún no hay períodos guardados. Ve a **Datos actuales**, filtra por fechas y haz clic en **Guardar período**.")
        else:
            snap_names = list(st.session_state.snapshots.keys())
            snap_sel = st.selectbox("Selecciona un período guardado:", snap_names, key="snap_sel")

            hcol1, hcol2 = st.columns([1, 1])
            with hcol1:
                if st.button("📂 Ver este período", use_container_width=True, key="btn_ver_snap"):
                    st.session_state["snap_activo"] = snap_sel
            with hcol2:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("🗑 Eliminar este período", use_container_width=True, key="btn_del_snap"):
                    del st.session_state.snapshots[snap_sel]
                    if st.session_state.get("snap_activo") == snap_sel:
                        del st.session_state["snap_activo"]
                    guardar_snapshots_disco()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # Mostrar snapshot activo
            if st.session_state.get("snap_activo") and st.session_state["snap_activo"] in st.session_state.snapshots:
                snap_activo = st.session_state["snap_activo"]
                df_snap_view = pd.read_csv(io.StringIO(st.session_state.snapshots[snap_activo]))
                df_snap_view["Fecha"] = pd.to_datetime(df_snap_view["Fecha"])

                st.success(f"📂 Mostrando: **{snap_activo}** — {len(df_snap_view)} registros")

                # KPIs del snapshot
                for col2 in ["Efectividad_Soles", "Tiempo_PDC"]:
                    if col2 in df_snap_view.columns:
                        df_snap_view[col2] = pd.to_numeric(df_snap_view[col2], errors="coerce").fillna(0)

                sv1, sv2, sv3, sv4 = st.columns(4)
                snap_ventas = df_snap_view["Efectividad_Soles"].sum() if "Efectividad_Soles" in df_snap_view.columns else 0
                snap_visitas = len(df_snap_view)
                snap_tiempo = df_snap_view["Tiempo_PDC"].mean() if "Tiempo_PDC" in df_snap_view.columns else 0
                snap_terceros = (df_snap_view["Colocacion_Terceros"] == "Sí").mean() * 100 if "Colocacion_Terceros" in df_snap_view.columns else 0
                for col_s, lbl, val, sub in [
                    (sv1, "Visitas", str(snap_visitas), "registros"),
                    (sv2, "Efectividad", f"S/ {snap_ventas:,.2f}", "total ventas"),
                    (sv3, "Tiempo Prom.", f"{snap_tiempo:.0f} min", "por visita"),
                    (sv4, "Con Terceros", f"{snap_terceros:.0f}%", "de visitas"),
                ]:
                    with col_s:
                        st.markdown(f"""<div class="kpi-box"><div class="kpi-label">{lbl}</div>
                            <div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>""",
                            unsafe_allow_html=True)

                st.markdown("")
                # Tabla del snapshot
                cols_snap = [c for c in ["Fecha","Codigo_PDC","Nombre_Cliente","Giro_Negocio",
                    "Vendedor","Zona","Efectividad_Soles","Tiempo_PDC","Colocacion_Terceros","Marca_Tercero"]
                    if c in df_snap_view.columns]
                st.dataframe(df_snap_view[cols_snap].sort_values("Fecha", ascending=False), use_container_width=True, hide_index=True)

                # Descargar snapshot como Excel
                snap_buf = io.BytesIO()
                with pd.ExcelWriter(snap_buf, engine="openpyxl") as writer:
                    df_snap_view.drop(columns=["Imagen_Path", "Concreto", "Fecha_str"], errors="ignore").to_excel(
                        writer, index=False, sheet_name="Historico"
                    )
                snap_buf.seek(0)
                st.download_button(
                    label=f"⬇️ Descargar Excel — {snap_activo}",
                    data=snap_buf,
                    file_name=f"historico_{snap_activo.replace(' ','_').replace('→','a')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    st.markdown("---")

    # Aplicar filtros para el resto del dashboard (datos actuales)
    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()
    mask = (df["Fecha"].dt.date >= fecha_desde) & (df["Fecha"].dt.date <= fecha_hasta)
    df_f = df[mask].copy()
    if filtro_vendedor != "Todos":
        df_f = df_f[df_f["Vendedor"] == filtro_vendedor]

    if df_f.empty:
        st.warning("No hay registros en el rango de fechas seleccionado.")
        st.stop()

    # ── TICKET PROMEDIO CALCULADO ─────────────────────────────────────────
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

    # ── TICKET PROMEDIO POR VENDEDOR ──────────────────────────────────────
    st.markdown("#### 📈 Ticket Promedio por Vendedor y Día")
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

    # ── FILA 1: Colocación Exhibidores + Giros + Terceros ─────────────────
    col_g1, col_g2, col_g3 = st.columns(3)

    with col_g1:
        st.markdown("#### 🗂️ Colocación Exhibidores")
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
        st.markdown("#### 🏬 Giros de Negocio")
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
        st.markdown("#### 🏷️ Colocación de Terceros")
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
                df_f["Marca_Tercero"] = df_f["Marca_Tercero"].astype(str)
                df_marcas = df_f[
                    (df_f["Colocacion_Terceros"] == "Sí") &
                    (df_f["Marca_Tercero"].str.strip().str.lower() != "nan") &
                    (df_f["Marca_Tercero"].str.strip() != "")
                ]["Marca_Tercero"].str.strip().str.upper().value_counts().reset_index()
                df_marcas.columns = ["Marca", "Visitas"]
                if not df_marcas.empty:
                    st.caption("Marcas detectadas")
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
        st.markdown("#### 📊 Efectividad")
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
        st.markdown("#### 📍 Mapa de Visitas")
        if "Latitud" in df_f.columns and "Longitud" in df_f.columns:
            df_map = df_f.copy()
            df_map["Latitud"] = pd.to_numeric(df_map["Latitud"], errors="coerce")
            df_map["Longitud"] = pd.to_numeric(df_map["Longitud"], errors="coerce")
            df_map = df_map.dropna(subset=["Latitud", "Longitud"])
            if not df_map.empty:
                zonas_unicas = df_map["Zona"].dropna().unique().tolist() if "Zona" in df_map.columns else []
                palette = ["#4472C4","#e05252","#6a9e4f","#FF7F0E","#7b5ea7","#FFBF00","#2196F3","#00BCD4"]
                zona_color = {z: palette[i % len(palette)] for i, z in enumerate(zonas_unicas)}
                df_map["_color"] = df_map["Zona"].map(zona_color).fillna("#888888")

                fig_map = go.Figure()

                for zona, grp in df_map.groupby("Zona"):
                    if len(grp) >= 1:
                        color_hex = zona_color.get(zona, "#888888")
                        r = int(color_hex[1:3], 16)
                        g = int(color_hex[3:5], 16)
                        b = int(color_hex[5:7], 16)
                        fig_map.add_trace(go.Scattermapbox(
                            lat=grp["Latitud"].tolist(),
                            lon=grp["Longitud"].tolist(),
                            mode="markers",
                            marker=dict(size=40, color=f"rgba({r},{g},{b},0.18)"),
                            hoverinfo="skip",
                            showlegend=False,
                            name=f"_sombra_{zona}"
                        ))

                for zona, grp in df_map.groupby("Zona"):
                    color_hex = zona_color.get(zona, "#888888")
                    giro_col = grp["Giro_Negocio"].str.replace(r"^\d+ - ", "", regex=True) if "Giro_Negocio" in grp.columns else grp.index.astype(str)
                    fig_map.add_trace(go.Scattermapbox(
                        lat=grp["Latitud"].tolist(),
                        lon=grp["Longitud"].tolist(),
                        mode="markers",
                        marker=dict(size=13, color=color_hex),
                        name=zona,
                        text=grp["Nombre_Cliente"].tolist(),
                        customdata=list(zip(
                            grp["Zona"].tolist(),
                            grp["Efectividad_Soles"].tolist(),
                            giro_col.tolist()
                        )),
                        hovertemplate=(
                            "<b>%{text}</b><br>"
                            "Zona: %{customdata[0]}<br>"
                            "Venta: S/ %{customdata[1]}<br>"
                            "Giro: %{customdata[2]}<extra></extra>"
                        )
                    ))

                lat_c = df_map["Latitud"].mean()
                lon_c = df_map["Longitud"].mean()
                lat_rng = df_map["Latitud"].max() - df_map["Latitud"].min()
                zoom_auto = 13 if lat_rng < 0.01 else (11 if lat_rng < 0.05 else 9)

                fig_map.update_layout(
                    mapbox=dict(style="open-street-map", center=dict(lat=lat_c, lon=lon_c), zoom=zoom_auto),
                    margin=dict(t=0, b=0, l=0, r=0),
                    height=380,
                    legend=dict(title="Zona", bgcolor="rgba(255,255,255,0.85)", bordercolor="#ddd", borderwidth=1),
                    font_family="DM Sans"
                )
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.info("Agrega visitas con latitud y longitud para ver el mapa.")

    st.markdown("---")

    # ── PRESENCIA DE PRODUCTOS ────────────────────────────────────────────
    st.markdown("#### 📦 Presencia de Productos (% de visitas)")
    productos = {
        "OREO_34GR": "OREO 34GR", "OREO_54GR": "OREO 54GR", "OREO_ROLLO": "OREO ROLLO",
        "RITZ_ROLLO": "RITZ ROLLO", "RITZ_TACO": "RITZ TACO",
        "FIELD_CC": "FIELD CC", "FIELD_DP": "FIELD DP", "FIELD_VAIN": "FIELD VAIN",
        "TRIDENT_5s": "TRIDENT 5s", "HALLS_12s": "HALLS 12s", "CHICLETS_2S": "CHICLETS 2S"
    }
    presencia_pct = []
    total_visitas_pres = len(df_f)
    for key, label in productos.items():
        if key in df_f.columns:
            serie = pd.to_numeric(df_f[key], errors="coerce")
            total_con = int(serie.sum())
            pct = serie.mean() * 100
            presencia_pct.append({
                "Producto": label,
                "Presencia %": round(pct, 1),
                "Total": total_con,
                "Etiqueta": f"{round(pct,1)}%  ({total_con}/{total_visitas_pres})"
            })
    df_pres = pd.DataFrame(presencia_pct).sort_values("Presencia %", ascending=False)
    fig_pres = px.bar(df_pres, x="Producto", y="Presencia %",
                      color="Presencia %",
                      color_continuous_scale=["#e8e6e0", "#7b5ea7"],
                      range_y=[0, 115],
                      text="Etiqueta",
                      custom_data=["Total", "Etiqueta"])
    fig_pres.update_traces(textposition="outside", textfont_size=10)
    fig_pres.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font_family="DM Sans",
        margin=dict(t=40, b=10, l=10, r=10),
        coloraxis_showscale=False,
        xaxis=dict(title="Producto", tickangle=-30),
        yaxis=dict(title="Presencia %", range=[0, 115])
    )
    st.plotly_chart(fig_pres, use_container_width=True)

    st.markdown("---")

    # ── TABLA ÚLTIMAS VISITAS ─────────────────────────────────────────────
    st.markdown("#### 📋 Últimas Visitas")
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
    st.markdown("#### ⬇️ Descargas")
    dcol1, dcol2 = st.columns(2)

    with dcol1:
        buffer = io.BytesIO()
        export_df = df_f.copy()
        export_df = export_df.merge(
            ticket_calc[["Vendedor", "Fecha_str", "Ticket_Calculado"]],
            left_on=["Vendedor", "Fecha_str"], right_on=["Vendedor", "Fecha_str"], how="left"
        )
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            export_df.drop(
                columns=["Imagen_Path", "Fecha_str", "Concreto"],
                errors="ignore"
            ).to_excel(writer, index=False, sheet_name="Visitas")
        buffer.seek(0)
        st.download_button(
            label="⬇️ Descargar Excel",
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
                label=f"🖼️ Descargar imágenes ({len(imagenes)} fotos)",
                data=zip_buffer,
                file_name=f"imagenes_MDZ_{date.today()}.zip",
                mime="application/zip",
                use_container_width=True
            )
        else:
            st.info("No hay imágenes guardadas aún.")
