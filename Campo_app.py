import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
import os
import io
import zipfile
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="SUPERVISIÓN CANAL TRADICIONAL MAU VERSION", layout="wide", page_icon=None)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background-color: #f5f4f0; }
    .block-container { padding: 2rem 2rem 2rem 2rem; }
    h1 { font-size: 1.6rem !important; font-weight: 600 !important; color: #1a1a1a !important; }
    h2 { font-size: 1.1rem !important; font-weight: 500 !important; color: #333 !important; }
    .kpi-box { background: white; border-radius: 12px; padding: 1.2rem 1.4rem; border: 1px solid #e8e6e0; }
    .kpi-label { font-size: 13px; text-transform: uppercase; letter-spacing: .08em; color: #888; margin-bottom: 4px; }
    .kpi-value { font-size: 32px; font-weight: 600; color: #1a1a1a; }
    .kpi-sub { font-size: 13px; color: #aaa; margin-top: 2px; }
    .stButton > button { background: #1a1a1a !important; color: white !important; border: none !important;
        border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important; padding: .6rem 2rem !important; font-size: 15px !important; }
    .stButton > button:hover { background: #333 !important; }
    div[data-testid="stCheckbox"] label { font-size: 13px !important; }
    .leyenda-box { background: #f0f0eb; border-radius: 8px; padding: .5rem 1rem; font-size: 13px; color: #666; margin-bottom: 12px; }
    .btn-danger > button { background: #e05252 !important; color: white !important; border: none !important; }
    .btn-danger > button:hover { background: #c0392b !important; }
    .seccion-inactiva { background: #f0f0eb; border-radius: 10px; padding: 1rem 1.4rem;
        border: 1px dashed #ccc; color: #aaa; font-size: 14px; text-align: center; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

CSV_FILE = "visitas.csv"
IMG_FOLDER = "imagenes_visita"
os.makedirs(IMG_FOLDER, exist_ok=True)

COLUMNAS = [
    "Fecha", "Codigo_PDC", "Nombre_Cliente", "Giro_Negocio",
    "Vendedor", "Codigo_Vendedor", "Mesa", "Zona", "Latitud", "Longitud",
    "OREO_34GR", "OREO_54GR", "OREO_ROLLO", "RITZ_ROLLO", "RITZ_PACK",
    "FIELD_CC", "FIELD_DP", "FIELD_VAIN", "CLUB_SOCIAL_TRA",
    "OREO_FRESA_PACK", "OREO_FRESA_ROLLO",
    "OREO_CHOCO_LIMON_PACK", "OREO_CHOCO_LIMON_ROLLO",
    "CLUB_SOCIAL_SAB", "ROLLO_GOLDEN", "ROLLO_CHOCOLATE",
    "TRIDENT_5s", "TRIDENT_EVUP", "HALLS_12s", "HALLS_100s", "CHICLETS_2S", "BUBBALOO",
    "LEGOS_GC", "TOBOGAN_RITZ_OREO", "EXHIB_KIWI", "RITRAZ", "MEGA_KIWI",
    "EXHIBIDOR_OTROS", "EXHIBIDOR_OTROS_DESC",
    "CONT_LEGOS_GC", "CONT_TOBOGAN_RITZ_OREO", "CONT_EXHIB_KIWI", "Causa_Contaminacion",
    "Visibilidad_Legos", "Visibilidad_Tobogan", "Visibilidad_Kiwi", "Visibilidad_Otros",
    "Visibilidad_Otros_Desc",
    "Colocacion_Terceros", "Marca_Tercero",
    "Efectividad_Soles", "Tiempo_PDC", "Imagen_Path",
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

for _k, _v in {
    "pagina": "formulario", "confirmar_eliminar": False, "gps_lat": "", "gps_lon": "",
    "snapshots": {}, "geo_resultados": [], "buscar_trigger": False,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

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

if not st.session_state.snapshots and os.path.exists(SNAPSHOTS_FILE):
    st.session_state.snapshots = cargar_snapshots_disco()


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL: GENERAR DASHBOARD EXCEL CON GRÁFICOS
# ═══════════════════════════════════════════════════════════════
def generar_dashboard_excel(df_f, ticket_calc, fecha_desde, fecha_hasta, filtro_vendedor,
                             total_visitas, total_ventas, ticket_prom_global,
                             tiempo_prom, pct_con_terceros, pct_concreto, data_exhib):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.drawing.image import Image as XLImage
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from collections import Counter

    PALETTE = ["#4472C4", "#e05252", "#6a9e4f", "#FF7F0E", "#7b5ea7",
               "#FFC107", "#00BCD4", "#FF69B4", "#8BC34A", "#FF5722",
               "#9C27B0", "#03A9F4", "#CDDC39", "#795548", "#607D8B"]

    thin   = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    dash_buf = io.BytesIO()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Dashboard Operativo"

    def insert_image_bytes(img_bytes, anchor_cell, width_px=480, height_px=320):
        img_io = io.BytesIO(img_bytes)
        img    = XLImage(img_io)
        img.width  = width_px
        img.height = height_px
        ws.add_image(img, anchor_cell)

    def fig_to_bytes(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor="white")
        buf.seek(0)
        return buf.read()

    def section_header(row, text, color="4472C4"):
        ws.merge_cells(f"A{row}:L{row}")
        c = ws.cell(row=row, column=1, value=text)
        c.font      = Font(bold=True, size=13, color="FFFFFF", name="Arial")
        c.fill      = PatternFill("solid", fgColor=color)
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[row].height = 26
        return row + 1

    def reserve_rows(start_row, n, height=15):
        for r in range(start_row, start_row + n):
            ws.row_dimensions[r].height = height
        return start_row + n

    IMG_FULL_W = 980
    IMG_HALF_W = 480
    IMG_H      = 330
    IMG_H_MAP  = 430
    IMG_H_WIDE = 330

    def chart_style(ax, title, ylabel="", xlabel=""):
        ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
        if ylabel: ax.set_ylabel(ylabel, fontsize=10)
        if xlabel: ax.set_xlabel(xlabel, fontsize=10)
        ax.yaxis.grid(True, linestyle="--", alpha=0.45, zorder=0)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # CABECERA
    ws.merge_cells("A1:L1")
    c = ws.cell(row=1, column=1,
                value="DASHBOARD OPERATIVO — SUPERVISIÓN CANAL TRADICIONAL")
    c.font      = Font(bold=True, size=18, color="FFFFFF", name="Arial")
    c.fill      = PatternFill("solid", fgColor="1a1a1a")
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 42

    ws.merge_cells("A2:L2")
    c2 = ws.cell(row=2, column=1,
                 value=f"Período: {fecha_desde}  →  {fecha_hasta}  |  Vendedor: {filtro_vendedor}")
    c2.font      = Font(size=12, color="555555", name="Arial")
    c2.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 22

    ws.merge_cells("A3:L3")
    c3 = ws.cell(row=3, column=1, value="INDICADORES CLAVE")
    c3.font      = Font(bold=True, size=13, color="FFFFFF", name="Arial")
    c3.fill      = PatternFill("solid", fgColor="4472C4")
    c3.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[3].height = 26

    kpi_data = [
        ("EFECTIVIDAD TOTAL (S/)", f"S/ {total_ventas:,.2f}",      "7b5ea7"),
        ("TICKET PROMEDIO (S/)",   f"S/ {ticket_prom_global:.2f}", "4472C4"),
        ("% CONCRETO VENTA",       f"{pct_concreto:.0f}%",         "6a9e4f"),
        ("TOTAL VISITAS",          str(total_visitas),             "FF7F0E"),
        ("TIEMPO PROM. PDC",       f"{tiempo_prom:.0f} min",       "e05252"),
        ("% CON TERCEROS",         f"{pct_con_terceros:.0f}%",     "FFC107"),
    ]
    ws.row_dimensions[4].height = 22
    ws.row_dimensions[5].height = 42
    ws.row_dimensions[6].height = 6

    for ci, (lbl, val, color) in enumerate(kpi_data, start=1):
        cs = (ci - 1) * 2 + 1
        ws.merge_cells(start_row=4, start_column=cs, end_row=4, end_column=cs + 1)
        cl = ws.cell(row=4, column=cs, value=lbl)
        cl.font      = Font(bold=True, size=10, color="FFFFFF", name="Arial")
        cl.fill      = PatternFill("solid", fgColor=color)
        cl.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.merge_cells(start_row=5, start_column=cs, end_row=5, end_column=cs + 1)
        cv = ws.cell(row=5, column=cs, value=val)
        cv.font      = Font(bold=True, size=20, color=color, name="Arial")
        cv.alignment = Alignment(horizontal="center", vertical="center")
        cv.fill      = PatternFill("solid", fgColor="F8F8F8")

    # TICKET TABLE
    row_cur = 7
    ws.merge_cells(f"A{row_cur}:L{row_cur}")
    ctk = ws.cell(row=row_cur, column=1, value="TICKET PROMEDIO POR VENDEDOR Y DÍA")
    ctk.font      = Font(bold=True, size=13, color="FFFFFF", name="Arial")
    ctk.fill      = PatternFill("solid", fgColor="4472C4")
    ctk.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row_cur].height = 24

    for ci, h in enumerate(["Vendedor", "Fecha", "Ventas del Día (S/)",
                             "Clientes Visitados", "Ticket Promedio (S/)"], 1):
        c = ws.cell(row=row_cur + 1, column=ci, value=h)
        c.font      = Font(bold=True, size=11, color="FFFFFF", name="Arial")
        c.fill      = PatternFill("solid", fgColor="6a9e4f")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border    = border
        ws.row_dimensions[row_cur + 1].height = 22

    alt_fill = PatternFill("solid", fgColor="F5F5F5")
    for ri, row_d in ticket_calc.iterrows():
        r = row_cur + 2 + ri
        for ci2, val in enumerate([row_d["Vendedor"], row_d["Fecha_str"],
                                    round(row_d["Ventas_Dia"], 2),
                                    int(row_d["Clientes_Dia"]),
                                    round(row_d["Ticket_Calculado"], 2)], 1):
            c = ws.cell(row=r, column=ci2, value=val)
            c.border    = border
            c.font      = Font(size=10, name="Arial")
            c.alignment = Alignment(horizontal="center", vertical="center")
            if ri % 2 == 1:
                c.fill = alt_fill
        ws.row_dimensions[r].height = 18

    row_cur = row_cur + 2 + len(ticket_calc) + 1

    # MAPA
    if "Latitud" in df_f.columns and "Longitud" in df_f.columns:
        df_map = df_f.copy()
        df_map["Latitud"]  = pd.to_numeric(df_map["Latitud"],  errors="coerce")
        df_map["Longitud"] = pd.to_numeric(df_map["Longitud"], errors="coerce")
        df_map = df_map.dropna(subset=["Latitud", "Longitud"])
        if not df_map.empty:
            row_cur = section_header(row_cur, "📍 MAPA DE VISITAS — DISTRIBUCIÓN GEOGRÁFICA", "4472C4")
            cs_map  = row_cur
            row_cur = reserve_rows(row_cur, 30, 15)
            zonas_u = df_map["Zona"].dropna().unique().tolist() if "Zona" in df_map.columns else ["Sin Zona"]
            zc_map  = {z: PALETTE[i % len(PALETTE)] for i, z in enumerate(zonas_u)}
            fig_m, ax_m = plt.subplots(figsize=(14, 6))
            for zona in zonas_u:
                grp = df_map[df_map["Zona"] == zona] if "Zona" in df_map.columns else df_map
                ax_m.scatter(grp["Longitud"], grp["Latitud"],
                             c=zc_map.get(zona, "#888"), s=100, label=zona,
                             alpha=0.88, edgecolors="white", linewidths=0.8, zorder=5)
            for _, rm in df_map.iterrows():
                ax_m.annotate(str(rm.get("Nombre_Cliente", ""))[:20],
                              (rm["Longitud"], rm["Latitud"]),
                              textcoords="offset points", xytext=(6, 4),
                              fontsize=7, alpha=0.8)
            chart_style(ax_m, "MAPA DE VISITAS — DISTRIBUCIÓN GEOGRÁFICA",
                        ylabel="Latitud", xlabel="Longitud")
            ax_m.legend(title="Zona", fontsize=9, title_fontsize=10,
                        loc="upper right", framealpha=0.9, edgecolor="#ccc")
            ax_m.grid(True, linestyle="--", alpha=0.35)
            plt.tight_layout()
            insert_image_bytes(fig_to_bytes(fig_m), f"A{cs_map}", IMG_FULL_W, IMG_H_MAP)
            plt.close(fig_m)
            row_cur += 1

    # GIRO + EFECTIVIDAD
    row_cur = section_header(row_cur, "GIRO DE NEGOCIO  |  EFECTIVIDAD DE VISITAS", "4472C4")
    cs_ge   = row_cur
    row_cur = reserve_rows(row_cur, 24, 15)

    if "Giro_Negocio" in df_f.columns:
        df_giro = df_f["Giro_Negocio"].value_counts().reset_index()
        df_giro.columns = ["Giro", "Visitas"]
        df_giro["Giro_Short"] = df_giro["Giro"].str.replace(r"^\d+ - ", "", regex=True)
        total_g = df_giro["Visitas"].sum()

        fig_gi, ax_gi = plt.subplots(figsize=(8, 5.5))
        wc = [PALETTE[i % len(PALETTE)] for i in range(len(df_giro))]
        wedges, _, autos = ax_gi.pie(
            df_giro["Visitas"], labels=None,
            autopct=lambda p: f"{p:.0f}%\n({int(round(p * total_g / 100))})",
            colors=wc, startangle=90, pctdistance=0.72,
            textprops={"fontsize": 9},
        )
        for at in autos:
            at.set_fontweight("bold")
        ax_gi.legend(wedges,
                     [f"{g}  ({v})" for g, v in zip(df_giro["Giro_Short"], df_giro["Visitas"])],
                     loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)
        ax_gi.set_title("GIROS DE NEGOCIO", fontsize=13, fontweight="bold", pad=10)
        plt.tight_layout()
        insert_image_bytes(fig_to_bytes(fig_gi), f"A{cs_ge}", IMG_HALF_W, IMG_H)
        plt.close(fig_gi)

    if "Concreto" in df_f.columns:
        df_ef  = df_f["Concreto"].value_counts().reset_index()
        df_ef.columns = ["Estado", "Cantidad"]
        total_ef = df_ef["Cantidad"].sum()

        fig_ef, ax_ef = plt.subplots(figsize=(8, 5.5))
        col_ef = ["#7b5ea7" if e == "CONCRETO" else "#e05252" for e in df_ef["Estado"]]
        bars_ef = ax_ef.barh(df_ef["Estado"], df_ef["Cantidad"],
                             color=col_ef, edgecolor="white", height=0.55)
        max_ef = df_ef["Cantidad"].max() if not df_ef.empty else 1
        for bar, cnt in zip(bars_ef, df_ef["Cantidad"]):
            pct = round(cnt / total_ef * 100) if total_ef > 0 else 0
            ax_ef.text(bar.get_width() + max_ef * 0.03,
                       bar.get_y() + bar.get_height() / 2,
                       f"{cnt}\n({pct}%)", va="center", ha="left",
                       fontsize=11, fontweight="bold")
        chart_style(ax_ef, "EFECTIVIDAD DE VISITAS", xlabel="Cantidad de Visitas")
        ax_ef.set_xlim(0, max_ef * 1.45)
        ax_ef.xaxis.grid(True, linestyle="--", alpha=0.45)
        plt.tight_layout()
        insert_image_bytes(fig_to_bytes(fig_ef), f"G{cs_ge}", IMG_HALF_W, IMG_H)
        plt.close(fig_ef)

    row_cur += 1

    # EXHIBIDORES
    exhib_cols_dict = {
        "LEGOS_GC": "LEGOS G&C", "TOBOGAN_RITZ_OREO": "TOBOGÁN Ritz/Oreo",
        "EXHIB_KIWI": "EXHIB KIWI", "RITRAZ": "RITRAZ",
        "MEGA_KIWI": "MEGA KIWI", "EXHIBIDOR_OTROS": "OTROS",
    }

    row_cur = section_header(row_cur, "COLOCACIÓN DE EXHIBIDORES  |  TIPO DE NEGOCIO POR EXHIBIDOR", "FF7F0E")
    cs_ex   = row_cur
    row_cur = reserve_rows(row_cur, 24, 15)

    labels_e = [d["Exhibidor"] for d in data_exhib]
    vals_e   = [d["Cantidad"]  for d in data_exhib]
    pcts_e   = [d["Pct"]       for d in data_exhib]
    max_e    = max(vals_e) if vals_e else 1

    fig_ex, ax_ex = plt.subplots(figsize=(10, 5))
    bars_ex = ax_ex.bar(labels_e, vals_e,
                        color=[PALETTE[i % len(PALETTE)] for i in range(len(labels_e))],
                        edgecolor="white", linewidth=1.2, zorder=3)
    for bar, cnt, pct in zip(bars_ex, vals_e, pcts_e):
        ax_ex.text(bar.get_x() + bar.get_width() / 2,
                   bar.get_height() + max_e * 0.025,
                   f"{cnt}\n({pct}%)",
                   ha="center", va="bottom", fontsize=10, fontweight="bold")
    chart_style(ax_ex, "COLOCACIÓN DE EXHIBIDORES", ylabel="Cantidad de Visitas")
    ax_ex.set_ylim(0, max_e * 1.4)
    plt.xticks(rotation=22, ha="right", fontsize=9)
    plt.tight_layout()
    insert_image_bytes(fig_to_bytes(fig_ex), f"A{cs_ex}", IMG_HALF_W, IMG_H)
    plt.close(fig_ex)

    import numpy as np
    exhib_giro_data = []
    for col_ex2, label_ex2 in exhib_cols_dict.items():
        if col_ex2 in df_f.columns and "Giro_Negocio" in df_f.columns:
            df_ex_s = df_f[pd.to_numeric(df_f[col_ex2], errors="coerce").fillna(0) > 0].copy()
            if df_ex_s.empty:
                continue
            df_ex_s["Giro_Short"] = (df_ex_s["Giro_Negocio"]
                                     .str.replace(r"^\d+ - ", "", regex=True)
                                     .str.strip())
            for giro, grp in df_ex_s.groupby("Giro_Short"):
                exhib_giro_data.append({"Exhibidor": label_ex2,
                                        "Giro": giro,
                                        "Cantidad": len(grp)})

    if exhib_giro_data:
        df_eg       = pd.DataFrame(exhib_giro_data)
        giros_u     = sorted(df_eg["Giro"].unique().tolist())
        exhibs_u    = list(exhib_cols_dict.values())
        exhibs_u    = [e for e in exhibs_u if e in df_eg["Exhibidor"].unique()]
        n_giros     = len(giros_u)
        n_exhibs    = len(exhibs_u)
        color_exhib = {e: PALETTE[i % len(PALETTE)] for i, e in enumerate(exhibs_u)}

        x_pos  = np.arange(n_giros)
        width  = 0.8 / max(n_exhibs, 1)

        fig_eg2, ax_eg2 = plt.subplots(figsize=(max(10, n_giros * 2.2), 5))

        for ei, exhib in enumerate(exhibs_u):
            vals_eg = []
            for giro in giros_u:
                sub = df_eg[(df_eg["Exhibidor"] == exhib) & (df_eg["Giro"] == giro)]
                vals_eg.append(int(sub["Cantidad"].sum()) if not sub.empty else 0)

            offset  = (ei - n_exhibs / 2 + 0.5) * width
            bars_eg = ax_eg2.bar(x_pos + offset, vals_eg,
                                 width * 0.92,
                                 label=exhib,
                                 color=color_exhib[exhib],
                                 edgecolor="white", linewidth=0.8, zorder=3)
            max_eg_val = max(vals_eg) if vals_eg else 1
            for bar, cnt in zip(bars_eg, vals_eg):
                if cnt > 0:
                    pct_eg = round(cnt / total_visitas * 100, 1)
                    ax_eg2.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max_eg_val * 0.04,
                        f"{cnt}\n({pct_eg}%)",
                        ha="center", va="bottom", fontsize=8, fontweight="bold"
                    )

        ax_eg2.set_xticks(x_pos)
        ax_eg2.set_xticklabels(giros_u, fontsize=9, rotation=15, ha="right")
        chart_style(ax_eg2, "COLOCACIÓN DE EXHIBIDORES POR GIRO DE NEGOCIO",
                    ylabel="Cantidad de Visitas")
        all_vals_eg = [v for row_d in exhib_giro_data for v in [row_d["Cantidad"]]]
        ax_eg2.set_ylim(0, (max(all_vals_eg) if all_vals_eg else 1) * 1.5)
        ax_eg2.legend(title="Exhibidor", fontsize=8, title_fontsize=9,
                      loc="upper right", ncol=2)
        plt.tight_layout()
        insert_image_bytes(fig_to_bytes(fig_eg2), f"G{cs_ex}", IMG_HALF_W, IMG_H)
        plt.close(fig_eg2)

    row_cur += 1

    # TERCEROS
    row_cur = section_header(row_cur, "COLOCACIÓN DE TERCEROS  |  MARCAS DE COMPETENCIA", "7b5ea7")
    cs_tc   = row_cur
    row_cur = reserve_rows(row_cur, 24, 15)

    if "Colocacion_Terceros" in df_f.columns and "Giro_Negocio" in df_f.columns:
        df_tg = df_f.copy()
        df_tg["Giro_Short"] = (df_tg["Giro_Negocio"]
                               .str.replace(r"^\d+ - ", "", regex=True).str.upper())
        df_con_t = (df_tg[df_tg["Colocacion_Terceros"] == "Sí"]
                    .groupby("Giro_Short").size().reset_index(name="N"))
        sin_n    = int((df_tg["Colocacion_Terceros"] != "Sí").sum())
        lbl_pie  = df_con_t["Giro_Short"].tolist() + ["SIN COLOCACION"]
        val_pie  = df_con_t["N"].tolist() + [sin_n]
        tot_pie  = sum(val_pie)
        col_pie  = [PALETTE[i % len(PALETTE)] for i in range(len(df_con_t))] + ["#4CAF50"]

        fig_tc, ax_tc = plt.subplots(figsize=(8, 5.5))
        wedges_t, _, autos_t = ax_tc.pie(
            val_pie, labels=None,
            autopct=lambda p: f"{p:.0f}%\n({int(round(p * tot_pie / 100))})",
            colors=col_pie, startangle=90, pctdistance=0.72,
            textprops={"fontsize": 9},
        )
        for at in autos_t:
            at.set_fontweight("bold")
        ax_tc.legend(wedges_t,
                     [f"{l}  ({v})" for l, v in zip(lbl_pie, val_pie)],
                     loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)
        ax_tc.set_title("COLOCACIÓN DE TERCEROS", fontsize=13, fontweight="bold", pad=10)
        plt.tight_layout()
        insert_image_bytes(fig_to_bytes(fig_tc), f"A{cs_tc}", IMG_HALF_W, IMG_H)
        plt.close(fig_tc)

    if "Marca_Tercero" in df_f.columns:
        df_mr = df_f[
            (df_f["Colocacion_Terceros"] == "Sí") &
            (df_f["Marca_Tercero"].astype(str).str.strip().str.lower() != "nan") &
            (df_f["Marca_Tercero"].astype(str).str.strip() != "")
        ]["Marca_Tercero"].copy()
        todas_m = []
        for v in df_mr:
            for m in str(v).split(","):
                mc = m.strip().upper()
                if mc and mc != "NAN":
                    todas_m.append(mc)
        if todas_m:
            cteo   = Counter(todas_m)
            df_mrc = pd.DataFrame(cteo.items(),
                                  columns=["Marca", "Cantidad"]).sort_values("Cantidad")
            tot_m  = df_mrc["Cantidad"].sum()
            df_mrc["Pct"] = (df_mrc["Cantidad"] / tot_m * 100).round(1)

            fig_mr, ax_mr = plt.subplots(
                figsize=(9, max(3.5, len(df_mrc) * 0.55 + 1.5)))
            bars_mr = ax_mr.barh(
                df_mrc["Marca"], df_mrc["Cantidad"],
                color=[PALETTE[i % len(PALETTE)] for i in range(len(df_mrc))],
                edgecolor="white")
            max_mr = df_mrc["Cantidad"].max() if not df_mrc.empty else 1
            for bar, cnt, pct in zip(bars_mr, df_mrc["Cantidad"], df_mrc["Pct"]):
                ax_mr.text(bar.get_width() + max_mr * 0.03,
                           bar.get_y() + bar.get_height() / 2,
                           f"{cnt}\n({pct}%)",
                           va="center", ha="left", fontsize=9, fontweight="bold")
            chart_style(ax_mr, "MARCAS DE COMPETENCIA EN PDV",
                        xlabel="Número de Visitas con Presencia")
            ax_mr.set_xlim(0, max_mr * 1.45)
            ax_mr.xaxis.grid(True, linestyle="--", alpha=0.45)
            plt.tight_layout()
            insert_image_bytes(fig_to_bytes(fig_mr), f"G{cs_tc}",
                               IMG_HALF_W,
                               int(max(3.5, len(df_mrc) * 0.55 + 1.5) * 72))
            plt.close(fig_mr)

    row_cur += 1

    # CONTAMINACIÓN + VISIBILIDAD
    row_cur = section_header(row_cur, "CONTAMINACIÓN DE EXHIBIDORES  |  VISIBILIDAD POR EXHIBIDOR", "e05252")
    cs_cv   = row_cur
    row_cur = reserve_rows(row_cur, 24, 15)

    cont_info = [("CONT_LEGOS_GC", "LEGOS G&C"),
                 ("CONT_TOBOGAN_RITZ_OREO", "TOBOGÁN Ritz/Oreo"),
                 ("CONT_EXHIB_KIWI", "EXHIB KIWI")]
    c_lbls, c_si, c_no, p_si, p_no = [], [], [], [], []
    for col_c, lbl_c in cont_info:
        if col_c in df_f.columns:
            sc  = pd.to_numeric(df_f[col_c], errors="coerce").fillna(0)
            si  = int(sc.sum())
            no  = len(sc) - si
            c_lbls.append(lbl_c); c_si.append(si); c_no.append(no)
            p_si.append(round(si / len(sc) * 100, 1) if len(sc) else 0)
            p_no.append(round(no / len(sc) * 100, 1) if len(sc) else 0)

    if c_lbls:
        xc   = np.arange(len(c_lbls))
        wc2  = 0.35
        maxc = max(c_si + c_no) if c_si + c_no else 1
        fig_ct, ax_ct = plt.subplots(figsize=(9, 5))
        b1 = ax_ct.bar(xc - wc2/2, c_si, wc2,
                       label="Contaminado", color="#e05252", edgecolor="white")
        b2 = ax_ct.bar(xc + wc2/2, c_no, wc2,
                       label="Limpio",      color="#4CAF50", edgecolor="white")
        for bar, cnt, pct in zip(b1, c_si, p_si):
            if cnt > 0:
                ax_ct.text(bar.get_x() + bar.get_width()/2,
                           bar.get_height() + maxc * 0.025,
                           f"{cnt}\n({pct}%)",
                           ha="center", va="bottom", fontsize=10, fontweight="bold")
        for bar, cnt, pct in zip(b2, c_no, p_no):
            if cnt > 0:
                ax_ct.text(bar.get_x() + bar.get_width()/2,
                           bar.get_height() + maxc * 0.025,
                           f"{cnt}\n({pct}%)",
                           ha="center", va="bottom", fontsize=10, fontweight="bold")
        ax_ct.set_xticks(xc)
        ax_ct.set_xticklabels(c_lbls, fontsize=10)
        chart_style(ax_ct, "CONTAMINACIÓN DE EXHIBIDORES",
                    ylabel="Cantidad de Visitas")
        ax_ct.set_ylim(0, maxc * 1.45)
        ax_ct.legend(fontsize=10)
        plt.tight_layout()
        insert_image_bytes(fig_to_bytes(fig_ct), f"A{cs_cv}", IMG_HALF_W, IMG_H)
        plt.close(fig_ct)

    vis_info = [("Visibilidad_Legos",   "LEGOS G&C"),
                ("Visibilidad_Tobogan", "TOBOGÁN Ritz/Oreo"),
                ("Visibilidad_Kiwi",    "EXHIB KIWI"),
                ("Visibilidad_Otros",   "OTROS")]
    v_alta, v_med, v_baj, v_lbls = [], [], [], []
    for col_v, lbl_v in vis_info:
        if col_v in df_f.columns:
            sv = pd.to_numeric(df_f[col_v], errors="coerce").fillna(0)
            v_alta.append(int((sv == 1).sum()))
            v_med.append(int((sv == 2).sum()))
            v_baj.append(int((sv == 3).sum()))
            v_lbls.append(lbl_v)

    if v_lbls:
        xv   = np.arange(len(v_lbls))
        wv   = 0.25
        maxv = max(v_alta + v_med + v_baj) if v_alta + v_med + v_baj else 1
        fig_vi, ax_vi = plt.subplots(figsize=(10, 5))
        ba = ax_vi.bar(xv - wv, v_alta, wv, label="Alta",  color="#4CAF50", edgecolor="white")
        bm = ax_vi.bar(xv,      v_med,  wv, label="Media", color="#FFC107", edgecolor="white")
        bb = ax_vi.bar(xv + wv, v_baj,  wv, label="Baja",  color="#e05252", edgecolor="white")
        for bars_v, data_v in [(ba, v_alta), (bm, v_med), (bb, v_baj)]:
            for bar, cnt in zip(bars_v, data_v):
                if cnt > 0:
                    pct_v = round(cnt / total_visitas * 100, 1)
                    ax_vi.text(bar.get_x() + bar.get_width()/2,
                               bar.get_height() + maxv * 0.025,
                               f"{cnt}\n({pct_v}%)",
                               ha="center", va="bottom", fontsize=8, fontweight="bold")
        ax_vi.set_xticks(xv)
        ax_vi.set_xticklabels(v_lbls, fontsize=10)
        chart_style(ax_vi, "VISIBILIDAD POR EXHIBIDOR",
                    ylabel="Cantidad de Visitas")
        ax_vi.set_ylim(0, maxv * 1.5)
        ax_vi.legend(title="Visibilidad", fontsize=10)
        plt.tight_layout()
        insert_image_bytes(fig_to_bytes(fig_vi), f"G{cs_cv}", IMG_HALF_W, IMG_H)
        plt.close(fig_vi)

    row_cur += 1

    # PRESENCIA DE PRODUCTOS
    productos_grupos = {
        "BISCUITS": {
            "OREO_34GR": "OREO 34GR", "OREO_54GR": "OREO 54GR", "OREO_ROLLO": "OREO ROLLO",
            "RITZ_ROLLO": "RITZ ROLLO", "RITZ_PACK": "RITZ PACK",
            "FIELD_CC": "FIELD CC", "FIELD_DP": "FIELD DP", "FIELD_VAIN": "FIELD VAIN",
            "CLUB_SOCIAL_TRA": "CLUB SOCIAL TRA",
        },
        "PRODUCTOS FOCO": {
            "OREO_FRESA_PACK": "OREO FRESA (Pack)", "OREO_FRESA_ROLLO": "OREO FRESA (Rollo)",
            "OREO_CHOCO_LIMON_PACK": "OREO CHOCO LIMÓN (Pack)",
            "OREO_CHOCO_LIMON_ROLLO": "OREO CHOCO LIMÓN (Rollo)",
            "CLUB_SOCIAL_SAB": "CLUB SOCIAL (Sabores)",
            "ROLLO_GOLDEN": "OREO GOLDEN (Rollo)", "ROLLO_CHOCOLATE": "OREO CHOCOLATE (Rollo)",
        },
        "G&C": {
            "TRIDENT_5s": "TRIDENT 5s", "TRIDENT_EVUP": "TRIDENT EVUP",
            "HALLS_12s": "HALLS 12s", "HALLS_100s": "HALLS 100s",
            "CHICLETS_2S": "CHICLETS 2S", "BUBBALOO": "BUBBALOO",
        },
    }

    row_cur = section_header(row_cur, "PRESENCIA DE PRODUCTOS (% DE VISITAS)", "1a1a1a")

    for gp_name, prods in productos_grupos.items():
        cs_pr   = row_cur
        row_cur = reserve_rows(row_cur, 22, 15)
        pres_d  = []
        for kp, lp in prods.items():
            if kp in df_f.columns:
                sp  = pd.to_numeric(df_f[kp], errors="coerce")
                cnt = int(sp.sum())
                pct = round(sp.mean() * 100, 1)
                pres_d.append({"Producto": lp, "Pct": pct, "Cnt": cnt})
        if not pres_d:
            row_cur += 1
            continue

        df_pr = pd.DataFrame(pres_d).sort_values("Pct", ascending=False)
        fig_pr, ax_pr = plt.subplots(figsize=(13, 5))
        bars_pr = ax_pr.bar(
            df_pr["Producto"], df_pr["Pct"],
            color=[PALETTE[i % len(PALETTE)] for i in range(len(df_pr))],
            edgecolor="white", linewidth=1, zorder=3)
        for bar, pct, cnt in zip(bars_pr, df_pr["Pct"], df_pr["Cnt"]):
            ax_pr.text(bar.get_x() + bar.get_width()/2,
                       bar.get_height() + 1.8,
                       f"{pct}%\n({cnt}/{total_visitas})",
                       ha="center", va="bottom", fontsize=9, fontweight="bold")
        chart_style(ax_pr, f"PRESENCIA DE PRODUCTOS — {gp_name}",
                    ylabel="Presencia %")
        ax_pr.set_ylim(0, 118)
        plt.xticks(rotation=22, ha="right", fontsize=9)
        plt.tight_layout()
        insert_image_bytes(fig_to_bytes(fig_pr), f"A{cs_pr}", IMG_FULL_W, IMG_H_WIDE)
        plt.close(fig_pr)
        row_cur += 1

    # TABLA ÚLTIMAS VISITAS
    row_cur = section_header(row_cur, "ÚLTIMAS VISITAS — DETALLE", "1a1a1a")
    cols_tbl = ["Fecha", "Codigo_PDC", "Nombre_Cliente", "Giro_Negocio", "Vendedor",
                "Zona", "Efectividad_Soles", "Tiempo_PDC",
                "Colocacion_Terceros", "Marca_Tercero"]
    cols_ex  = [c for c in cols_tbl if c in df_f.columns]
    df_tbl   = df_f[cols_ex].sort_values("Fecha", ascending=False).head(100)

    hdr_cols = ["4472C4", "4472C4", "4472C4", "6a9e4f", "6a9e4f",
                "FF7F0E", "7b5ea7", "e05252", "FFC107", "FFC107"]
    for ci, col_n in enumerate(cols_ex, 1):
        c = ws.cell(row=row_cur, column=ci, value=col_n.replace("_", " ").upper())
        hc = hdr_cols[ci - 1] if ci - 1 < len(hdr_cols) else "4472C4"
        c.font      = Font(bold=True, size=10, color="FFFFFF", name="Arial")
        c.fill      = PatternFill("solid", fgColor=hc)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border    = border
    ws.row_dimensions[row_cur].height = 22
    row_cur += 1

    alt_fill2 = PatternFill("solid", fgColor="F5F5F5")
    for ri, (_, rd) in enumerate(df_tbl.iterrows()):
        for ci, col_n in enumerate(cols_ex, 1):
            val = rd[col_n]
            if pd.isna(val): val = ""
            c = ws.cell(row=row_cur, column=ci, value=val)
            c.font      = Font(size=10, name="Arial")
            c.border    = border
            c.alignment = Alignment(horizontal="center", vertical="center")
            if ri % 2 == 1:
                c.fill = alt_fill2
        ws.row_dimensions[row_cur].height = 16
        row_cur += 1

    for col_l, w in {"A": 32, "B": 18, "C": 18, "D": 18, "E": 18, "F": 18,
                     "G": 32, "H": 18, "I": 18, "J": 18, "K": 18, "L": 18}.items():
        ws.column_dimensions[col_l].width = w

    ws_raw  = wb.create_sheet("Datos Completos")
    exp_df  = df_f.copy()
    exp_df  = exp_df.merge(ticket_calc[["Vendedor", "Fecha_str", "Ticket_Calculado"]],
                           on=["Vendedor", "Fecha_str"], how="left")
    cols_rw = [c for c in exp_df.columns
               if c not in ["Imagen_Path", "Fecha_str", "Concreto"]]
    for ci, col_n in enumerate(cols_rw, 1):
        c = ws_raw.cell(row=1, column=ci, value=col_n)
        c.font      = Font(bold=True, size=11, color="FFFFFF", name="Arial")
        c.fill      = PatternFill("solid", fgColor="1a1a1a")
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws_raw.column_dimensions[get_column_letter(ci)].width = 18
    for ri, (_, rd) in enumerate(exp_df[cols_rw].iterrows(), 2):
        for ci, val in enumerate(rd, 1):
            if pd.isna(val): val = ""
            ws_raw.cell(row=ri, column=ci, value=val).font = Font(size=10, name="Arial")

    wb.save(dash_buf)
    dash_buf.seek(0)
    return dash_buf


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

    st.markdown("### 📍 Ubicación del PDC")

    if st.session_state.gps_lat and st.session_state.gps_lon:
        lugar_guardado = st.session_state.get("gps_lugar", "")
        if lugar_guardado:
            st.success(f"✅ Ubicación guardada: {lugar_guardado} | Coordenadas: {st.session_state.gps_lat}, {st.session_state.gps_lon}")
        else:
            st.success(f"✅ Ubicación guardada: {st.session_state.gps_lat}, {st.session_state.gps_lon}")
        if st.button("Cambiar ubicación"):
            st.session_state.gps_lat = ""
            st.session_state.gps_lon = ""
            st.session_state.geo_resultados = []
            if "map_click" in st.session_state:
                del st.session_state["map_click"]
            st.rerun()
    else:
        if "ajuste_manual" not in st.session_state:
            st.session_state["ajuste_manual"] = False

        col_tog1, col_tog2 = st.columns([1, 3])
        with col_tog1:
            if st.session_state["ajuste_manual"]:
                if st.button("🔒 Desactivar ajuste", key="btn_toggle_ajuste", use_container_width=True):
                    st.session_state["ajuste_manual"] = False
                    st.rerun()
            else:
                if st.button("✏️ Ajuste manual", key="btn_toggle_ajuste", use_container_width=True):
                    st.session_state["ajuste_manual"] = True
                    st.rerun()
        with col_tog2:
            if st.session_state["ajuste_manual"]:
                st.success("✅ Modo ajuste activo — mueve el mapa hasta centrar el pin rojo en el PDC y presiona 'Obtener ubicación'")
            else:
                st.info("ℹ️ Activa el ajuste manual para mover el marcador al PDC")

        center = st.session_state.get("map_center", [-8.111801, -79.028678])
        zoom   = st.session_state.get("map_zoom", 15)
        m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")

        if not st.session_state["ajuste_manual"]:
            folium.Marker(
                location=center, draggable=False,
                tooltip="📍 Activa el ajuste manual para ubicar el PDC",
                icon=folium.Icon(color="gray", icon="map-marker", prefix="fa"),
            ).add_to(m)

        if st.session_state["ajuste_manual"]:
            m.get_root().html.add_child(folium.Element("""
            <style>
            .crosshair-shadow { position:absolute;top:50%;left:50%;transform:translate(-50%,2px);width:14px;height:6px;background:rgba(0,0,0,0.25);border-radius:50%;z-index:9999;pointer-events:none; }
            .crosshair-pin { position:absolute;top:50%;left:50%;transform:translate(-50%,-100%);z-index:9999;pointer-events:none;animation:bounce 1.2s infinite ease-in-out; }
            .crosshair-lines { position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:60px;height:60px;z-index:9998;pointer-events:none; }
            @keyframes bounce { 0%,100%{transform:translate(-50%,-100%)}50%{transform:translate(-50%,-115%)} }
            </style>
            <div class="crosshair-shadow"></div>
            <div class="crosshair-pin"><svg width="36" height="48" viewBox="0 0 36 48" xmlns="http://www.w3.org/2000/svg"><filter id="shadow"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="rgba(0,0,0,0.3)"/></filter><path d="M18 0C8.059 0 0 8.059 0 18c0 12 18 30 18 30S36 30 36 18C36 8.059 27.941 0 18 0z" fill="#e05252" filter="url(#shadow)"/><circle cx="18" cy="18" r="8" fill="white"/><circle cx="18" cy="18" r="4.5" fill="#e05252"/></svg></div>
            <svg class="crosshair-lines" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"><line x1="0" y1="30" x2="22" y2="30" stroke="#e05252" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.6"/><line x1="38" y1="30" x2="60" y2="30" stroke="#e05252" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.6"/><line x1="30" y1="0" x2="30" y2="22" stroke="#e05252" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.6"/><line x1="30" y1="38" x2="30" y2="60" stroke="#e05252" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.6"/></svg>
            """))

        map_data = st_folium(m, height=420, use_container_width=True, key="folium_map", returned_objects=["center", "zoom"])

        if map_data and map_data.get("center"):
            c = map_data["center"]
            st.session_state["map_center_actual"] = [round(c["lat"], 6), round(c["lng"], 6)]

        if st.session_state["ajuste_manual"]:
            col_ob1, col_ob2 = st.columns([2, 3])
            with col_ob1:
                st.caption("Mueve el mapa hasta centrar el punto rojo en el PDC")
            with col_ob2:
                if st.button("📌 Obtener ubicación del centro", key="btn_obtener_ubi", use_container_width=True):
                    pos = st.session_state.get("map_center_actual") or center
                    lat_nuevo = round(pos[0], 6)
                    lon_nuevo = round(pos[1], 6)
                    st.session_state["map_click"] = (lat_nuevo, lon_nuevo)
                    st.session_state["map_center"] = [lat_nuevo, lon_nuevo]
                    with st.spinner("Obteniendo nombre del lugar..."):
                        try:
                            import requests as _req
                            r = _req.get("https://nominatim.openstreetmap.org/reverse",
                                params={"lat": lat_nuevo, "lon": lon_nuevo, "format": "json", "accept-language": "es", "zoom": 18},
                                headers={"User-Agent": "MDZ-SupervisionApp/1.0"}, timeout=6)
                            if r.status_code == 200:
                                addr = r.json().get("address", {})
                                nombre = (addr.get("road") or addr.get("pedestrian") or addr.get("neighbourhood") or addr.get("suburb") or addr.get("town") or addr.get("city") or "Ubicación seleccionada")
                                ciudad = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or ""
                                distrito = addr.get("suburb") or addr.get("neighbourhood") or ""
                                partes = [p for p in [distrito, ciudad] if p and p != nombre]
                                st.session_state["map_lugar"] = ", ".join([nombre] + partes[:2])
                            else:
                                st.session_state["map_lugar"] = ""
                        except Exception:
                            st.session_state["map_lugar"] = ""
                    st.rerun()

        if st.session_state.get("map_click"):
            lat_click, lon_click = st.session_state["map_click"]
            lugar = st.session_state.get("map_lugar", "")
            st.markdown("---")
            col_info1, col_info2 = st.columns([3, 1])
            with col_info1:
                if lugar:
                    st.markdown(f"""<div style="background:#f0f4ff;border:1px solid #c5d0e8;border-radius:8px;padding:10px 14px;">
                        <div style="font-size:11px;color:#666;text-transform:uppercase;letter-spacing:.05em;margin-bottom:2px;">Ubicación seleccionada</div>
                        <div style="font-size:15px;font-weight:600;color:#1a1a1a;">📍 {lugar}</div>
                        <div style="font-size:12px;color:#888;margin-top:2px;">{lat_click}, {lon_click}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div style="background:#f0f4ff;border:1px solid #c5d0e8;border-radius:8px;padding:10px 14px;">
                        <div style="font-size:11px;color:#666;text-transform:uppercase;letter-spacing:.05em;margin-bottom:2px;">Ubicación seleccionada</div>
                        <div style="font-size:15px;font-weight:600;color:#1a1a1a;">📍 {lat_click}, {lon_click}</div>
                    </div>""", unsafe_allow_html=True)
            with col_info2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅ Confirmar punto", key="geo_map_ok", use_container_width=True):
                    st.session_state.gps_lat = str(lat_click)
                    st.session_state.gps_lon = str(lon_click)
                    lugar_final = st.session_state.get("map_lugar", "")
                    if not lugar_final:
                        with st.spinner("Obteniendo nombre..."):
                            try:
                                import requests as _req
                                r = _req.get("https://nominatim.openstreetmap.org/reverse",
                                    params={"lat": lat_click, "lon": lon_click, "format": "json", "accept-language": "es", "zoom": 18},
                                    headers={"User-Agent": "MDZ-SupervisionApp/1.0"}, timeout=6)
                                if r.status_code == 200:
                                    addr = r.json().get("address", {})
                                    nombre = (addr.get("road") or addr.get("pedestrian") or addr.get("neighbourhood") or addr.get("suburb") or addr.get("town") or addr.get("city") or "Ubicación seleccionada")
                                    ciudad = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or ""
                                    distrito = addr.get("suburb") or addr.get("neighbourhood") or ""
                                    partes = [p for p in [nombre, distrito, ciudad] if p and p != nombre]
                                    lugar_final = ", ".join([nombre] + partes[:2])
                            except Exception:
                                lugar_final = ""
                    st.session_state["gps_lugar"] = lugar_final
                    st.session_state["ajuste_manual"] = False
                    st.session_state.pop("map_click", None)
                    st.session_state.pop("map_lugar", None)
                    st.rerun()

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════
    # SELECTORES FUERA DEL FORM — Vendedor → Cliente (cascada reactiva)
    # ══════════════════════════════════════════════════════════════════════
    df_hist = cargar_datos()

    st.markdown("### 🧑‍💼 Ruta")
    vendedores_lista = sorted(df_hist["Vendedor"].dropna().unique().tolist()) if not df_hist.empty else []
    vendedores_opciones = ["✏️ Escribir nuevo vendedor..."] + vendedores_lista

    col_sv1, col_sv2, col_sv3 = st.columns(3)
    with col_sv1:
        sel_vendedor = st.selectbox(
            "Nombre del Vendedor",
            vendedores_opciones,
            key="sel_vendedor_drop",
        )
        if sel_vendedor == "✏️ Escribir nuevo vendedor...":
            vendedor = st.text_input(
                "Escribir nombre del vendedor",
                placeholder="Nombre completo...",
                key="txt_vendedor_nuevo",
            )
        else:
            vendedor = sel_vendedor
    with col_sv2:
        codigo_vendedor_pre = ""
        if vendedor and not df_hist.empty:
            fila_vend = df_hist[df_hist["Vendedor"] == vendedor]
            if not fila_vend.empty and "Codigo_Vendedor" in fila_vend.columns:
                codigo_vendedor_pre = str(fila_vend.iloc[0]["Codigo_Vendedor"] or "")
        codigo_vendedor = st.text_input(
            "Código de Vendedor",
            value=codigo_vendedor_pre,
            max_chars=8,
            placeholder="Ej: VEN00001",
            key="cod_vend_input",
        )
    with col_sv3:
        mesa_pre = ""
        if vendedor and not df_hist.empty:
            fila_vend = df_hist[df_hist["Vendedor"] == vendedor]
            if not fila_vend.empty and "Mesa" in fila_vend.columns:
                mesa_pre = str(fila_vend.iloc[0]["Mesa"] or "")
        mesa = st.text_input(
            "Mesa",
            value=mesa_pre,
            placeholder="Ej: DJ1, DJ3...",
            key="txt_mesa_input",
        )
    ruta_logica_pre = ""
    ruta_logica = st.text_input("Ruta Lógica", value=ruta_logica_pre, placeholder="Ej: Ruta 01 - Norte", key="ruta_logica_input")

    st.markdown("---")

    # ── Selector de Cliente filtrado por vendedor ──────────────────────────
    st.markdown("### 🏪 Datos del Cliente")

    clientes_del_vendedor = []
    if vendedor and not df_hist.empty:
        df_vend_hist = df_hist[df_hist["Vendedor"] == vendedor].copy()
        # Agrupar por PDC para obtener la última visita (nombre + código más reciente)
        if not df_vend_hist.empty:
            df_vend_hist["Fecha"] = pd.to_datetime(df_vend_hist["Fecha"])
            df_ult = (df_vend_hist.sort_values("Fecha", ascending=False)
                      .drop_duplicates(subset=["Codigo_PDC"])
                      [["Codigo_PDC", "Nombre_Cliente", "Giro_Negocio", "Zona"]]
                      .dropna(subset=["Codigo_PDC"]))
            for _, row in df_ult.iterrows():
                etiqueta = f"{row['Codigo_PDC']} — {row['Nombre_Cliente']}"
                clientes_del_vendedor.append({
                    "etiqueta": etiqueta,
                    "codigo_pdc": str(row["Codigo_PDC"]),
                    "nombre_cliente": str(row["Nombre_Cliente"]),
                    "giro_negocio": str(row.get("Giro_Negocio", "")),
                    "zona": str(row.get("Zona", "")),
                })

    opciones_cliente = ["✏️ Nuevo cliente (no registrado)"] + [c["etiqueta"] for c in clientes_del_vendedor]

    col_sc1, col_sc2 = st.columns([3, 1])
    with col_sc1:
        sel_cliente = st.selectbox(
            "Seleccionar Cliente",
            opciones_cliente,
            key="sel_cliente_drop",
            help="Filtra los clientes visitados por este vendedor. Elige 'Nuevo cliente' para ingresar uno nuevo.",
        )

    # Determinar valores pre-cargados según selección
    if sel_cliente == "✏️ Nuevo cliente (no registrado)":
        prefill_codigo   = ""
        prefill_nombre   = ""
        prefill_giro     = "Selecciona..."
        prefill_zona     = ""
        es_cliente_nuevo = True
    else:
        match = next((c for c in clientes_del_vendedor if c["etiqueta"] == sel_cliente), None)
        prefill_codigo   = match["codigo_pdc"]   if match else ""
        prefill_nombre   = match["nombre_cliente"] if match else ""
        prefill_giro     = match["giro_negocio"]  if match else "Selecciona..."
        prefill_zona     = match["zona"]          if match else ""
        es_cliente_nuevo = False

    with st.form("form_visita", clear_on_submit=False):

        col1, col2, col3 = st.columns(3)
        with col1: fecha = st.date_input("Fecha de Visita", value=date.today())
        with col2:
            codigo_pdc = st.text_input(
                "Código PDC (8 dígitos)",
                value=prefill_codigo,
                max_chars=8,
                placeholder="Ej: 00000001",
                disabled=not es_cliente_nuevo,
            )
        with col3:
            nombre_cliente = st.text_input(
                "Nombre del Cliente",
                value=prefill_nombre,
                placeholder="Ej: Bodega Central",
                disabled=not es_cliente_nuevo,
            )

        # ── Si no hay nombre de cliente, mostrar campo alternativo ──────────
        if es_cliente_nuevo and not nombre_cliente.strip():
            st.markdown(
                '<div style="background:#fff8e1;border:1px solid #ffe082;border-radius:8px;'
                'padding:8px 14px;font-size:13px;color:#7a6000;margin-bottom:8px;">'
                '⚠️ Si el cliente no tiene nombre registrado, completa el campo alternativo.'
                '</div>',
                unsafe_allow_html=True,
            )
            col_alt1, col_alt2 = st.columns([2, 1])
            with col_alt1:
                nombre_alternativo = st.text_input(
                    "Descripción / Nombre alternativo",
                    placeholder="Ej: Bodega esquina Jr. Las Flores...",
                    key="nombre_alt",
                )
            with col_alt2:
                referencia_extra = st.text_input(
                    "Referencia adicional (opcional)",
                    placeholder="Ej: frente al parque, piso 2...",
                    key="ref_extra",
                )
            if nombre_alternativo.strip() and referencia_extra.strip():
                nombre_cliente_final = f"{nombre_alternativo.strip()} — {referencia_extra.strip()}"
            elif nombre_alternativo.strip():
                nombre_cliente_final = nombre_alternativo.strip()
            else:
                nombre_cliente_final = "SIN NOMBRE"
        else:
            nombre_cliente_final = nombre_cliente.strip() if nombre_cliente.strip() else prefill_nombre

        giro_opciones = [
            "Selecciona...", "1 - Bodega", "2 - Minimarket / Tiendas", "3 - Kiosko",
            "4 - Especializados (Panificadora, Horeca, Internet...)",
            "5 - Otros (Puesto de mercado, Centros Educativos...)"
        ]
        giro_index = giro_opciones.index(prefill_giro) if prefill_giro in giro_opciones else 0

        col4, col5 = st.columns(2)
        with col4:
            giro_negocio = st.selectbox("Giro de Negocio", giro_opciones, index=giro_index)
        with col5:
            zona = st.text_input("Zona", value=prefill_zona, placeholder="Ej: TRUJILLO CENTRO, VICTOR LARCO...")

        latitud  = st.session_state.gps_lat
        longitud = st.session_state.gps_lon

        # Vendedor y Mesa vienen de fuera del form (session state ya los tiene)
        st.markdown("---")
        st.markdown("### 🧑‍💼 Ruta (confirmación)")
        col_rv1, col_rv2, col_rv3 = st.columns(3)
        with col_rv1:
            st.text_input("Vendedor (seleccionado)", value=vendedor, disabled=True, key="vend_confirm")
        with col_rv2:
            st.text_input("Código Vendedor (confirmación)", value=codigo_vendedor, disabled=True, key="codvend_confirm")
        with col_rv3:
            st.text_input("Mesa (confirmación)", value=mesa, disabled=True, key="mesa_confirm")
        ruta_logica_form = st.text_input("Ruta Lógica (confirmación)", value=ruta_logica, disabled=True, key="ruta_confirm")

        st.markdown("---")
        st.markdown("### 🍪 Presencia Biscuits")
        biscuits = {
            "OREO_34GR": "OREO 34GR", "OREO_54GR": "OREO 54GR", "OREO_ROLLO": "OREO ROLLO",
            "RITZ_ROLLO": "RITZ ROLLO", "RITZ_PACK": "RITZ PACK",
            "FIELD_CC": "FIELD (CC)", "FIELD_DP": "FIELD (DP)", "FIELD_VAIN": "FIELD (VAIN)",
            "CLUB_SOCIAL_TRA": "CLUB SOCIAL (TRA)",
        }
        cols_b = st.columns(5)
        biscuits_vals = {}
        for i, (key, label) in enumerate(biscuits.items()):
            with cols_b[i % 5]:
                biscuits_vals[key] = st.checkbox(label, key=f"b_{key}")

        st.markdown("---")
        st.markdown("### ⭐ Productos Foco")
        productos_foco = {
            "OREO_FRESA_PACK":        "OREO FRESA (Pack)",
            "OREO_FRESA_ROLLO":       "OREO FRESA (Rollo)",
            "OREO_CHOCO_LIMON_PACK":  "OREO CHOCO LIMÓN (Pack)",
            "OREO_CHOCO_LIMON_ROLLO": "OREO CHOCO LIMÓN (Rollo)",
            "CLUB_SOCIAL_SAB":        "CLUB SOCIAL (Sabores)",
            "ROLLO_GOLDEN":           "OREO GOLDEN (Rollo)",
            "ROLLO_CHOCOLATE":        "OREO CHOCOLATE (Rollo)",
        }
        cols_pf = st.columns(3)
        pf_vals = {}
        for i, (key, label) in enumerate(productos_foco.items()):
            with cols_pf[i % 3]:
                pf_vals[key] = st.checkbox(label, key=f"pf_{key}")

        st.markdown("---")
        st.markdown("### 🍬 Presencia G&C")
        gyc = {
            "TRIDENT_5s": "TRIDENT 5s", "TRIDENT_EVUP": "TRIDENT EVUP",
            "HALLS_12s": "HALLS 12s", "HALLS_100s": "HALLS 100s",
            "CHICLETS_2S": "CHICLETS 2S", "BUBBALOO": "BUBBALOO",
        }
        cols2 = st.columns(6)
        gyc_vals = {}
        for i, (key, label) in enumerate(gyc.items()):
            with cols2[i % 6]:
                gyc_vals[key] = st.checkbox(label, key=f"g_{key}")

        st.markdown("---")
        st.markdown("### 🗂️ Tipos de Exhibidores")
        tipos = {
            "LEGOS_GC": "LEGOS G&C", "TOBOGAN_RITZ_OREO": "TOBOGÁN (Ritz/Oreo)",
            "EXHIB_KIWI": "EXHIB KIWI", "RITRAZ": "RITRAZ",
            "MEGA_KIWI": "MEGA KIWI", "EXHIBIDOR_OTROS": "OTROS",
        }
        cols3 = st.columns(3)
        tipos_vals = {}
        for i, (key, label) in enumerate(tipos.items()):
            with cols3[i % 3]:
                tipos_vals[key] = st.checkbox(label, key=f"t_{key}")
        exhibidor_otros_desc = st.text_input(
            "Especificar otro exhibidor (si marcó OTROS)",
            placeholder="Ej: Stand especial, Canastilla...",
            key="exhib_otros_desc"
        )

        # ── Mapeo: qué exhibidores tienen contaminación y visibilidad ──────
        # Solo estos 3 tienen lógica de contaminación
        EXHIB_CONT = {
            "LEGOS_GC":          ("LEGOS G&C",           "cr_legos",   "CONT_LEGOS_GC"),
            "TOBOGAN_RITZ_OREO": ("TOBOGÁN (Ritz/Oreo)", "cr_tobogan", "CONT_TOBOGAN_RITZ_OREO"),
            "EXHIB_KIWI":        ("EXHIB KIWI",           "cr_kiwi",   "CONT_EXHIB_KIWI"),
        }
        # Todos los exhibidores tienen visibilidad (incluyendo OTROS como grupo)
        EXHIB_VIS = {
            "LEGOS_GC":          ("LEGOS G&C",           "vl", "Visibilidad_Legos"),
            "TOBOGAN_RITZ_OREO": ("TOBOGÁN (Ritz/Oreo)", "vt", "Visibilidad_Tobogan"),
            "EXHIB_KIWI":        ("EXHIB KIWI",           "vk", "Visibilidad_Kiwi"),
            "EXHIBIDOR_OTROS":   ("OTROS",                "vo", "Visibilidad_Otros"),
        }

        # Qué exhibidores están seleccionados ahora mismo
        exhibs_seleccionados = [k for k, v in tipos_vals.items() if v]
        hay_exhib = len(exhibs_seleccionados) > 0

        # ────────────────────────────────────────────────────────────────────
        # SECCIÓN: CONTAMINACIÓN (solo si hay exhibidores con cont. marcados)
        # ────────────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### ⚠️ Contaminación de Exhibidores")

        exhibs_cont_activos = [k for k in exhibs_seleccionados if k in EXHIB_CONT]

        if not hay_exhib:
            st.markdown(
                '<div class="seccion-inactiva">🔒 Selecciona al menos un tipo de exhibidor para activar esta sección</div>',
                unsafe_allow_html=True
            )
            cont_legos   = "No"
            cont_tobogan = "No"
            cont_kiwi    = "No"
            causa_contaminacion = ""
        else:
            if not exhibs_cont_activos:
                st.info("ℹ️ Los exhibidores seleccionados (RITRAZ, MEGA KIWI, OTROS) no aplican para contaminación.")
                cont_legos   = "No"
                cont_tobogan = "No"
                cont_kiwi    = "No"
                causa_contaminacion = ""
            else:
                # Mostrar solo los radios de los exhibidores marcados que tienen cont.
                n_cont = len(exhibs_cont_activos)
                cols_cont = st.columns(n_cont)
                cont_respuestas = {}
                for idx, k in enumerate(exhibs_cont_activos):
                    label_c, radio_key, _ = EXHIB_CONT[k]
                    with cols_cont[idx]:
                        cont_respuestas[k] = st.radio(
                            label_c, ["No", "Sí"], horizontal=True, key=radio_key
                        )

                # Rellenar los no-mostrados con "No"
                cont_legos   = cont_respuestas.get("LEGOS_GC",          "No")
                cont_tobogan = cont_respuestas.get("TOBOGAN_RITZ_OREO", "No")
                cont_kiwi    = cont_respuestas.get("EXHIB_KIWI",        "No")

                causa_contaminacion = ""
                if any(v == "Sí" for v in cont_respuestas.values()):
                    causa_contaminacion = st.text_input(
                        "Causa de contaminación",
                        placeholder="Describe la causa...",
                        key="causa_cont"
                    )

        cont_vals = {
            "CONT_LEGOS_GC":          1 if cont_legos   == "Sí" else 0,
            "CONT_TOBOGAN_RITZ_OREO": 1 if cont_tobogan == "Sí" else 0,
            "CONT_EXHIB_KIWI":        1 if cont_kiwi    == "Sí" else 0,
        }

        # ────────────────────────────────────────────────────────────────────
        # SECCIÓN: VISIBILIDAD (solo si hay exhibidores marcados)
        # ────────────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 👁️ Visibilidad por Exhibidor")

        VIS_OPTIONS = [1, 2, 3]
        VIS_LABELS  = {1: "1 - Alta", 2: "2 - Media", 3: "3 - Baja"}

        # Valores por defecto
        vis_legos   = 1
        vis_tobogan = 1
        vis_kiwi    = 1
        vis_otros   = 1
        vis_otros_desc = ""

        if not hay_exhib:
            st.markdown(
                '<div class="seccion-inactiva">🔒 Selecciona al menos un tipo de exhibidor para activar esta sección</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown('<div class="leyenda-box">1 = Alta &nbsp;|&nbsp; 2 = Media &nbsp;|&nbsp; 3 = Baja</div>',
                        unsafe_allow_html=True)

            exhibs_vis_activos = [k for k in exhibs_seleccionados if k in EXHIB_VIS]

            if not exhibs_vis_activos:
                st.info("ℹ️ Los exhibidores seleccionados no aplican para visibilidad.")
            else:
                n_vis = len(exhibs_vis_activos)
                cols_vis = st.columns(n_vis)
                vis_respuestas = {}
                for idx, k in enumerate(exhibs_vis_activos):
                    label_v, radio_key_v, _ = EXHIB_VIS[k]
                    with cols_vis[idx]:
                        vis_respuestas[k] = st.radio(
                            label_v, VIS_OPTIONS,
                            format_func=lambda x: VIS_LABELS[x],
                            horizontal=True, key=radio_key_v
                        )

                vis_legos   = vis_respuestas.get("LEGOS_GC",          1)
                vis_tobogan = vis_respuestas.get("TOBOGAN_RITZ_OREO", 1)
                vis_kiwi    = vis_respuestas.get("EXHIB_KIWI",        1)
                vis_otros   = vis_respuestas.get("EXHIBIDOR_OTROS",   1)

                if "EXHIBIDOR_OTROS" in exhibs_vis_activos:
                    vis_otros_desc = st.text_input(
                        "Descripción de OTROS (visibilidad)",
                        placeholder="Ej: Exhibidor especial...",
                        key="vis_otros_desc"
                    )

        st.markdown("---")
        st.markdown("### 🏷️ Colocación de Terceros")
        col_terc1, col_terc2 = st.columns([1, 3])
        with col_terc1:
            colocacion_terceros = st.radio("¿Hay colocación de terceros?", ["No", "Sí"], horizontal=True)
        with col_terc2:
            t1, t2, t3, t4 = st.columns(4)
            with t1: marca_tercero_1 = st.text_input("Marca 1", placeholder="Ej: Alicorp", key="mt1")
            with t2: marca_tercero_2 = st.text_input("Marca 2", placeholder="Ej: Molitalia", key="mt2")
            with t3: marca_tercero_3 = st.text_input("Marca 3", placeholder="Ej: Costa", key="mt3")
            with t4: marca_tercero_4 = st.text_input("Marca 4", placeholder="Ej: Nestlé", key="mt4")
        marca_tercero = ", ".join([m for m in [marca_tercero_1, marca_tercero_2, marca_tercero_3, marca_tercero_4] if m.strip()])

        st.markdown("---")
        st.markdown("### 📊 Indicadores de la visita")
        k1, k2 = st.columns(2)
        with k1: efectividad_soles = st.number_input("Efectividad (S/)", min_value=0.0, step=1.0, value=0.0, format="%.2f")
        with k2: tiempo_pdc = st.number_input("Tiempo en PDC (minutos)", min_value=0, step=1, value=0)

        st.markdown("---")
        st.markdown("### 📝 Detalles IG")
        detalles_ig = st.text_area("Detalles IG", placeholder="Ingresa los detalles IG...", height=100, label_visibility="collapsed")

        st.markdown("---")
        st.markdown("### 📷 Evidencia fotográfica")
        st.caption("Puedes subir hasta 5 fotos por visita (JPG, PNG)")
        imagen_1 = st.file_uploader("Foto 1", type=["jpg", "jpeg", "png"], key="img1")
        imagen_2 = st.file_uploader("Foto 2", type=["jpg", "jpeg", "png"], key="img2")
        imagen_3 = st.file_uploader("Foto 3", type=["jpg", "jpeg", "png"], key="img3")
        imagen_4 = st.file_uploader("Foto 4", type=["jpg", "jpeg", "png"], key="img4")
        imagen_5 = st.file_uploader("Foto 5", type=["jpg", "jpeg", "png"], key="img5")

        st.markdown("---")
        submitted = st.form_submit_button("💾 Guardar registro", use_container_width=True)

        if submitted:
            if not codigo_pdc or giro_negocio == "Selecciona...":
                st.error("Por favor completa el Código PDC y el Giro de Negocio.")
            else:
                img_paths = []
                nombre_limpio = nombre_cliente_final.replace(" ", "_").replace("/", "-").replace("\u2014", "-")[:40]
                for idx, img_file in enumerate([imagen_1, imagen_2, imagen_3, imagen_4, imagen_5], start=1):
                    if img_file is not None:
                        ext = img_file.name.rsplit(".", 1)[-1].lower()
                        img_filename = f"{nombre_limpio}_{str(fecha)}_foto{idx}.{ext}"
                        img_path_full = os.path.join(IMG_FOLDER, img_filename)
                        with open(img_path_full, "wb") as fout:
                            fout.write(img_file.getbuffer())
                        img_paths.append(img_path_full)

                img_path_guardado = "|".join(img_paths) if img_paths else ""
                registro = {
                    "Fecha": str(fecha), "Codigo_PDC": codigo_pdc,
                    "Nombre_Cliente": nombre_cliente_final, "Giro_Negocio": giro_negocio,
                    "Vendedor": vendedor, "Codigo_Vendedor": codigo_vendedor,
                    "Mesa": mesa, "Zona": zona, "Latitud": latitud, "Longitud": longitud,
                    **{k: int(v) for k, v in biscuits_vals.items()},
                    **{k: int(v) for k, v in pf_vals.items()},
                    **{k: int(v) for k, v in gyc_vals.items()},
                    **{k: int(v) for k, v in tipos_vals.items()},
                    "EXHIBIDOR_OTROS_DESC": exhibidor_otros_desc,
                    **{k: int(v) for k, v in cont_vals.items()},
                    "Causa_Contaminacion": causa_contaminacion,
                    "Visibilidad_Legos":      vis_legos,
                    "Visibilidad_Tobogan":    vis_tobogan,
                    "Visibilidad_Kiwi":       vis_kiwi,
                    "Visibilidad_Otros":      vis_otros,
                    "Visibilidad_Otros_Desc": vis_otros_desc,
                    "Colocacion_Terceros": colocacion_terceros,
                    "Marca_Tercero":       marca_tercero,
                    "Efectividad_Soles":   efectividad_soles,
                    "Tiempo_PDC":          tiempo_pdc,
                    "Imagen_Path":         img_path_guardado,
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
            st.session_state.pagina = "formulario"; st.rerun()
    with col_btn2:
        if st.button("＋ Nueva visita"):
            st.session_state.pagina = "formulario"; st.rerun()
    with col_btn3:
        if not st.session_state.confirmar_eliminar:
            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
            if st.button("🗑️ Eliminar historial"):
                st.session_state.confirmar_eliminar = True; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("¿Seguro? Esta acción no se puede deshacer.")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("Confirmar eliminación"):
                    eliminar_historial(); st.session_state.confirmar_eliminar = False
                    st.session_state.pagina = "formulario"; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                if st.button("Cancelar"):
                    st.session_state.confirmar_eliminar = False; st.rerun()

    if df.empty:
        st.warning("No hay registros aún.")
        st.stop()

    df["Fecha"] = pd.to_datetime(df["Fecha"])
    for col in ["Efectividad_Soles", "Tiempo_PDC"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    st.markdown("---")
    st.markdown("#### 📅 Filtros y datos históricos")

    tab_actual, tab_historial = st.tabs(["📊 Datos actuales", "🗂️ Historial guardado"])

    with tab_actual:
        fecha_min = df["Fecha"].min().date()
        fecha_max = df["Fecha"].max().date()
        col_f1, col_f2, col_f3 = st.columns([2, 2, 3])
        with col_f1: fecha_desde = st.date_input("Desde", value=fecha_min, min_value=fecha_min, max_value=fecha_max, key="fd")
        with col_f2: fecha_hasta = st.date_input("Hasta", value=fecha_max, min_value=fecha_min, max_value=fecha_max, key="fh")
        with col_f3:
            vendedores_disponibles = ["Todos"] + sorted(df["Vendedor"].dropna().unique().tolist())
            filtro_vendedor = st.selectbox("Filtrar por Vendedor", vendedores_disponibles)

        st.markdown("---")
        st.markdown("##### 💾 Guardar este período como histórico")
        sc1, sc2 = st.columns([3, 1])
        with sc1:
            nombre_snap = st.text_input("Nombre del período",
                placeholder=f"Ej: Semana del {fecha_desde} al {fecha_hasta}",
                key="snap_nombre", label_visibility="collapsed")
        with sc2:
            if st.button("💾 Guardar período", use_container_width=True, key="btn_guardar_snap"):
                mask_snap = (df["Fecha"].dt.date >= fecha_desde) & (df["Fecha"].dt.date <= fecha_hasta)
                df_snap = df[mask_snap].copy()
                if filtro_vendedor != "Todos":
                    df_snap = df_snap[df_snap["Vendedor"] == filtro_vendedor]
                if df_snap.empty:
                    st.warning("No hay datos en este rango.")
                else:
                    snap_key = nombre_snap.strip() if nombre_snap.strip() else f"{fecha_desde} → {fecha_hasta}"
                    if filtro_vendedor != "Todos": snap_key += f" ({filtro_vendedor})"
                    st.session_state.snapshots[snap_key] = df_snap.to_csv(index=False)
                    guardar_snapshots_disco()
                    st.success(f"✅ Guardado: *{snap_key}* ({len(df_snap)} registros)")

    with tab_historial:
        if not st.session_state.snapshots:
            st.info("Aún no hay períodos guardados.")
        else:
            snap_names = list(st.session_state.snapshots.keys())
            snap_sel = st.selectbox("Selecciona un período guardado:", snap_names, key="snap_sel")
            hcol1, hcol2 = st.columns([1, 1])
            with hcol1:
                if st.button("📂 Ver este período", use_container_width=True, key="btn_ver_snap"):
                    st.session_state["snap_activo"] = snap_sel
            with hcol2:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("🗑️ Eliminar este período", use_container_width=True, key="btn_del_snap"):
                    del st.session_state.snapshots
