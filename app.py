import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ----------------------------------------------------
st.set_page_config(
    page_title="Healthlytics",
    page_icon="logo/logo.png",
    layout="wide",
)

# Tema visual suave
st.markdown("""
<style>
body {
    background-color: #FFEFA0;
}
.block-container {
    padding-top: 1rem;
}
h1, h2, h3 {
    color: #5A8F68;
}
</style>
""", unsafe_allow_html=True)

plt.style.use("seaborn-v0_8-whitegrid") 
plt.style.use("ggplot")

# ----------------------------------------------------
# CARGA DE DATOS
# ----------------------------------------------------
@st.cache_data
def load_data(path="Life Expectancy Data.csv"):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Filtrar países
countries = ["Costa Rica", "Panama"]
df_ca = df[df["Country"].isin(countries)].copy()
df_ca.columns = df_ca.columns.str.strip()

# Columnas a limpiar
cols = [
    "Year", "Life expectancy", "Adult Mortality", "infant deaths", "Alcohol",
    "percentage expenditure", "Hepatitis B", "Measles", "BMI", "under-five deaths",
    "Polio", "Total expenditure", "Diphtheria", "HIV/AIDS", "GDP", "Population",
    "thinness  1-19 years", "thinness 5-9 years",
    "Income composition of resources", "Schooling"
]

# Convertir a numérico y rellenar NA por promedio
for col in cols:
    df_ca[col] = pd.to_numeric(df_ca[col], errors="coerce")
    df_ca[col] = df_ca.groupby("Country")[col].transform(lambda x: x.fillna(x.mean()))

# ----------------------------------------------------
# FILTRO INTERACTIVO POR PAÍS
# ----------------------------------------------------
st.sidebar.header("Filtro por país")
country_filter = st.sidebar.selectbox("Selecciona un país:", ["Todos"] + countries)

if country_filter != "Todos":
    df_display = df_ca[df_ca["Country"] == country_filter]
else:
    df_display = df_ca

# ----------------------------------------------------
# FILTRO INTERACTIVO POR AÑO (2000-2015)
# ----------------------------------------------------
st.sidebar.header("Filtro por año")
year_min, year_max = st.sidebar.slider(
    "Selecciona el rango de años:",
    min_value=int(df_ca["Year"].min()),
    max_value=int(df_ca["Year"].max()),
    value=(2000, 2015)
)

# Filtrado general por rango de años para gráficas y tabla
df_display = df_display[(df_display["Year"] >= year_min) & (df_display["Year"] <= year_max)]
df_filtered = df_ca[(df_ca["Year"] >= year_min) & (df_ca["Year"] <= year_max)]


# ----------------------------------------------------
# TÍTULO PRINCIPAL
# ----------------------------------------------------
st.title("📊 Healthlytics Dashboard")
st.subheader("“¿Por qué Costa Rica tiene mayor esperanza de vida que Panamá?”")

st.write("""
A través de este dashboard analizaremos los factores que explican por qué Costa Rica mantiene 
una esperanza de vida más alta que Panamá a lo largo del tiempo. Cada gráfica responde una parte 
de esta pregunta hasta llegar a una conclusión final basada en datos.
""")

st.divider()

# ----------------------------------------------------
# KPIs - Diferencias entre Costa Rica y Panamá
# ----------------------------------------------------
# Filtrar por país y años
df_cr = df_ca[(df_ca["Country"]=="Costa Rica") & (df_ca["Year"]>=year_min) & (df_ca["Year"]<=year_max)]
df_pa = df_ca[(df_ca["Country"]=="Panama") & (df_ca["Year"]>=year_min) & (df_ca["Year"]<=year_max)]

# Calcular diferencias
life_diff = df_cr["Life expectancy"].mean() - df_pa["Life expectancy"].mean()
gdp_diff = df_cr["GDP"].mean() - df_pa["GDP"].mean()
schooling_diff = df_cr["Schooling"].mean() - df_pa["Schooling"].mean()

# Mostrar KPIs
st.subheader("📊 KPIs: Diferencias entre Costa Rica y Panamá")
col1, col2, col3 = st.columns(3)
col1.metric("Diferencia en Esperanza de Vida (años)", f"{life_diff:.2f}")
col2.metric("Diferencia en PIB (USD promedio)", f"${gdp_diff:.2f}")
col3.metric("Diferencia en Escolaridad (años)", f"{schooling_diff:.2f}")

st.sidebar.markdown("Muestra la información filtrada por país.")

# ----------------------------------------------------
# Cifras generales de comparación
# ----------------------------------------------------
st.subheader("📌 Comparación de cifras clave")

# Esperanza de vida
avg_life = df_filtered.groupby("Country")["Life expectancy"].mean()
diff_life = avg_life["Costa Rica"] - avg_life["Panama"]

# GDP
avg_gdp = df_filtered.groupby("Country")["GDP"].mean()
diff_gdp = avg_gdp["Costa Rica"] - avg_gdp["Panama"]

# Cobertura de vacunación
vac_cols = ["Hepatitis B", "Polio", "Diphtheria"]
avg_vac = df_filtered.groupby("Country")[vac_cols].mean()

st.markdown(f"""
**Esperanza de vida promedio:**  
- Costa Rica: {avg_life['Costa Rica']:.2f} años  
- Panamá: {avg_life['Panama']:.2f} años  
- **Diferencia:** {diff_life:.2f} años

**GDP promedio:**  
- Costa Rica: ${avg_gdp['Costa Rica']:.2f}  
- Panamá: ${avg_gdp['Panama']:.2f}  
- **Diferencia:** ${diff_gdp:.2f}

**Cobertura promedio de vacunación:**  
- Hepatitis B: Costa Rica {avg_vac['Hepatitis B']['Costa Rica']:.1f}% vs Panamá {avg_vac['Hepatitis B']['Panama']:.1f}%  
- Polio: Costa Rica {avg_vac['Polio']['Costa Rica']:.1f}% vs Panamá {avg_vac['Polio']['Panama']:.1f}%  
- Difteria: Costa Rica {avg_vac['Diphtheria']['Costa Rica']:.1f}% vs Panamá {avg_vac['Diphtheria']['Panama']:.1f}%
""")

st.divider()

# ----------------------------------------------------
# GRÁFICA 1 - Tendencia de esperanza de vida
# ----------------------------------------------------
st.subheader("📈 1. Tendencia de esperanza de vida")
fig1, ax1 = plt.subplots(figsize=(10,4))
for country in df_display["Country"].unique():
    data = df_display[df_display["Country"] == country]
    ax1.plot(data["Year"], data["Life expectancy"], marker="o", label=country, linewidth=2)
ax1.set_xlabel("Año")
ax1.set_ylabel("Esperanza de vida (Años)")
ax1.grid(alpha=0.3)
ax1.legend()
st.pyplot(fig1)

st.markdown("""
<div style="padding:12px; border-radius:10px; background:#FFEFA0;">
Costa Rica mantiene una ventaja constante sobre Panamá a través del tiempo.
</div>
""", unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------
# GRÁFICA 2 - Economía (GDP)
# ----------------------------------------------------
st.subheader("💰 2. ¿La economía explica la diferencia?")
df_gdp = df_display.groupby("Country")["GDP"].mean().sort_values()  
fig2, ax2 = plt.subplots(figsize=(8,4))
ax2.barh(df_gdp.index, df_gdp.values)
ax2.set_xlabel("GDP Promedio")
ax2.set_title("GDP promedio por país")
for i, v in enumerate(df_gdp.values):
    ax2.text(v + 0.5, i, f"{v:.2f}", color='black', va='center')
st.pyplot(fig2)

st.markdown("""
<div style="padding:12px; border-radius:10px; background:#FFEFA0;">
Aunque Panamá presenta un GDP similar o mayor, esto no se traduce en mejores indicadores de salud pública.
</div>
""", unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------
# GRÁFICA 3 - Salud preventiva (Vacunación)
# ----------------------------------------------------
st.subheader("💉 3. Programas de vacunación")

df_vac = df_display.groupby("Country")[vac_cols].mean()

fig3, ax3 = plt.subplots(figsize=(10,4))
df_vac.plot(kind="bar", ax=ax3)

ax3.set_ylabel("Cobertura promedio (%)")
ax3.set_title("Cobertura de vacunación promedio")
ax3.grid(alpha=0.3)

st.pyplot(fig3)

st.markdown(f"""
<div style="padding:12px; border-radius:10px; background:#FFEFA0;">
Costa Rica presenta mejores programas de vacunación:
- Hepatitis B: {avg_vac['Hepatitis B']['Costa Rica']:.1f}% vs {avg_vac['Hepatitis B']['Panama']:.1f}%  
- Polio: {avg_vac['Polio']['Costa Rica']:.1f}% vs {avg_vac['Polio']['Panama']:.1f}%  
- Difteria: {avg_vac['Diphtheria']['Costa Rica']:.1f}% vs {avg_vac['Diphtheria']['Panama']:.1f}%
</div>
""", unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------
# GRÁFICA 4 - Educación
# ----------------------------------------------------
st.subheader("🎓 4. Educación vs esperanza de vida")
fig4, ax4 = plt.subplots(figsize=(10,5))
scatter = ax4.scatter(
    df_display["Schooling"],  
    df_display["Life expectancy"],
    c=df_display["Income composition of resources"],
    cmap="viridis",
    s=80,
    alpha=0.8
)
ax4.set_xlabel("Años de escolaridad")
ax4.set_ylabel("Esperanza de vida (años)")
ax4.grid(alpha=0.3)
plt.colorbar(scatter, label="Índice educativo / ingreso")
st.pyplot(fig4)

st.markdown("""
<div style="padding:12px; border-radius:10px; background:#FFEFA0;">
Costa Rica tiene mayor escolaridad y mejor índice social: esto impacta directamente la esperanza de vida.
</div>
""", unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------
# GRÁFICA 5 - Correlaciones
# ----------------------------------------------------
st.subheader("🔬 5. Factores que influyen más en la esperanza de vida")
corr = df_display[cols].corr()  
fig5, ax5 = plt.subplots(figsize=(10,6))
sns.heatmap(corr, cmap="viridis", annot=False)
st.pyplot(fig5)

st.divider()

# ----------------------------------------------------
# GRÁFICA 6 - Variabilidad en mortalidad
# ----------------------------------------------------
st.subheader("⚠️ 6. Variabilidad en mortalidad")

fig6, ax6 = plt.subplots(1, 2, figsize=(12, 5))

sns.boxplot(data=df_display, x="Country", y="Adult Mortality", ax=ax6[0])
ax6[0].set_title("Mortalidad Adulta")
ax6[0].set_ylabel("Tasa")

sns.boxplot(data=df_display, x="Country", y="infant deaths", ax=ax6[1])
ax6[1].set_title("Mortalidad Infantil")
ax6[1].set_ylabel("Número de muertes")

st.pyplot(fig6)

st.markdown("""
<div style="padding:12px; background:#FFEFA0; border-radius:10px;">
Panamá muestra mayor variabilidad en mortalidad adulta e infantil, lo cual afecta negativamente su esperanza de vida.
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# TABLA CON FILTRO POR PAÍS
# ----------------------------------------------------
st.subheader("📂 Datos detallados por país")
st.dataframe(df_display)

st.divider()

# ----------------------------------------------------
# CONCLUSIÓN FINAL
# ----------------------------------------------------
st.subheader("Conclusión final")

st.markdown(f"""
<div style="padding:20px; border-radius:12px; background:#B8D39D;">

<h3>¿Por qué Costa Rica tiene mayor esperanza de vida que Panamá?</h3>

- Mantiene **mayor escolaridad**, lo que se asocia fuertemente con mejores condiciones de salud.
- Posee **mejor cobertura de vacunación** (Hepatitis B, Polio y Difteria), reflejando un sistema preventivo más sólido.
- Tiene un **modelo de salud más preventivo y consistente**.
- Presenta **menor variabilidad en mortalidad adulta e infantil**, lo que estabiliza sus indicadores de salud a lo largo del tiempo.

<h3>Lo que NO explica la diferencia:</h3>
- El GDP, dado que Panamá tiene niveles similares o incluso superiores, por lo que la economía no es el factor determinante.

<h2><b>Conclusión general: </b></h2>
educación + salud preventiva + estabilidad en mortalidad = mayor esperanza de vida.

</div>
""", unsafe_allow_html=True)
