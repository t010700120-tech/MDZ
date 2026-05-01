# ================= AÑADIR EN FORMULARIO (ANTES DEL BOTÓN) =================

st.markdown("---")
st.markdown("### 🧁 Categorías")

c1, c2, c3 = st.columns(3)

with c1:
    oreo_34 = st.checkbox("OREO 34GR")
    oreo_54 = st.checkbox("OREO 54GR")
    oreo_rollo = st.checkbox("OREO ROLLO")

with c2:
    ritz_rollo = st.checkbox("RITZ ROLLO")
    ritz_taco = st.checkbox("RITZ TACO")
    club_tra = st.checkbox("CLUB SOCIAL TRA")

with c3:
    club_sab = st.checkbox("CLUB SOCIAL SAB")
    trident = st.checkbox("TRIDENT")
    halls = st.checkbox("HALLS")

st.markdown("### 🧱 Exhibidores")

e1, e2 = st.columns(2)

with e1:
    legos = st.number_input("LEGOS GC", min_value=0)
    tobogan = st.number_input("TOBOGAN", min_value=0)
    kiwi = st.number_input("KIWI", min_value=0)

with e2:
    cont_legos = st.number_input("CONT LEGOS", min_value=0)
    cont_tobogan = st.number_input("CONT TOBOGAN", min_value=0)
    cont_kiwi = st.number_input("CONT KIWI", min_value=0)

terceros = st.selectbox("¿Colocación de terceros?", ["Sí","No"])


# ================= MODIFICAR SOLO EL REGISTRO =================

registro.update({
    "OREO_34GR": int(oreo_34),
    "OREO_54GR": int(oreo_54),
    "OREO_ROLLO": int(oreo_rollo),
    "RITZ_ROLLO": int(ritz_rollo),
    "RITZ_TACO": int(ritz_taco),
    "CLUB_SOCIAL_TRA": int(club_tra),
    "CLUB_SOCIAL_SAB": int(club_sab),
    "TRIDENT_5s": int(trident),
    "HALLS_12s": int(halls),

    "LEGOS_GC": legos,
    "TOBOGAN_RITZ_OREO": tobogan,
    "EXHIB_KIWI": kiwi,

    "CONT_LEGOS_GC": cont_legos,
    "CONT_TOBOGAN_RITZ_OREO": cont_tobogan,
    "CONT_EXHIB_KIWI": cont_kiwi,

    "Colocacion_Terceros": terceros
})


# ================= AÑADIR EN DASHBOARD =================

# 🔥 LIMPIEZA
df["Efectividad"] = pd.to_numeric(df["Efectividad"], errors="coerce").fillna(0)

# 🔥 CIERRE
df["Cierre"] = df["Efectividad"] > 0

# 🔥 COBERTURA
biscuits_cols = [
    "OREO_34GR","OREO_54GR","OREO_ROLLO",
    "RITZ_ROLLO","RITZ_TACO",
    "CLUB_SOCIAL_TRA","CLUB_SOCIAL_SAB"
]

gomas_cols = [
    "TRIDENT_5s","TRIDENT_EVUP",
    "HALLS_12s","HALLS_100s","CHICLETS_2S"
]

df["BISCUITS"] = df[biscuits_cols].sum(axis=1) > 0
df["GOMAS"] = df[gomas_cols].sum(axis=1) > 0

st.markdown("### 📊 Cobertura")
st.write("Biscuits:", round(df["BISCUITS"].mean()*100,1), "%")
st.write("Gomas GYC:", round(df["GOMAS"].mean()*100,1), "%")

# 🔥 EXHIBIDORES
st.markdown("### 🧱 Exhibidores")

total_exhib = df[["LEGOS_GC","TOBOGAN_RITZ_OREO","EXHIB_KIWI"]].sum().sum()
contaminados = df[["CONT_LEGOS_GC","CONT_TOBOGAN_RITZ_OREO","CONT_EXHIB_KIWI"]].sum().sum()

st.write("Total:", int(total_exhib))
st.write("Contaminados:", int(contaminados))

# 🔥 TERCEROS
st.markdown("### 🧃 Terceros")

terceros_count = df["Colocacion_Terceros"].value_counts()
st.write(terceros_count)

# 🔥 GIRO VS EXHIBIDORES
st.markdown("### 🏪 Exhibidores por giro")

df["TOTAL_EXHIB"] = df[["LEGOS_GC","TOBOGAN_RITZ_OREO","EXHIB_KIWI"]].sum(axis=1)

fig = px.bar(df, x="Giro_Negocio", y="TOTAL_EXHIB")
st.plotly_chart(fig, use_container_width=True)

# 🔥 EFECTIVIDAD REAL
st.markdown("### 📈 Cierre de ventas")

cierre_df = df.groupby("Nombre_Vendedor")["Cierre"].mean().reset_index()

fig2 = px.bar(cierre_df, x="Nombre_Vendedor", y="Cierre")
st.plotly_chart(fig2, use_container_width=True)
