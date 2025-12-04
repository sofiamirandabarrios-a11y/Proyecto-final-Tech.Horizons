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

plt.style.use("seaborn-whitegrid")

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

st.sidebar.markdown("Muestra la información filtrada por país.")

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
# Cifras generales de comparación
# ----------------------------------------------------
st.subheader("📌 Comparación de cifras clave")

# Esperanza de vida
avg_life = df_ca.groupby("Country")["Life expectancy"].mean()
diff_life = avg_life["Costa Rica"] - avg_life["Panama"]

# GDP
avg_gdp = df_ca.groupby("Country")["GDP"].mean()
diff_gdp = avg_gdp["Costa Rica"] - avg_gdp["Panama"]

# Cobertura de vacunación
vac_cols = ["Hepatitis B", "Polio", "Diphtheria"]
avg_vac = df_ca.groupby("Country")[vac_cols].mean()

st.markdown(f"""
**Esperanza de vida promedio:**  
- Costa Rica: {avg_life['Costa Rica']:.2f} años  
- Panamá: {avg_life['Panama']:.2f} años  
**Diferencia:** {diff_life:.2f} años

**GDP promedio:**  
- Costa Rica: ${avg_gdp['Costa Rica']:.2f}  
- Panamá: ${avg_gdp['Panama']:.2f}  
**Diferencia:** ${diff_gdp:.2f}

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
for country in countries:
    data = df_ca[df_ca["Country"] == country]
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
df_gdp = df_ca.groupby("Country")["GDP"].mean().sort_values()
fig2, ax2 = plt.subplots(figsize=(8,4))
ax2.barh(df_gdp.index, df_gdp.values)
ax2.set_xlabel("GDP Promedio")
ax2.set_title("GDP promedio por país")
# Mostrar valores encima de las barras
for i, v in enumerate(df_gdp.values):
    ax2.text(v + 0.5, i, f"{v:.2f}", color='black', va='center')
st.pyplot(fig2)

st.markdown("""
<div style="padding:12px; border-radius:10px; background:#FFEFA0;">
El GDP no explica la diferencia en esperanza de vida: Panamá incluso tiene niveles similares o mayores.
</div>
""", unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------
# GRÁFICA 3 - Salud preventiva (Vacunación)
# ----------------------------------------------------
st.subheader("💉 3. Programas de vacunación")
df_vac = df_ca.groupby("Country")[vac_cols].mean()
fig3, ax3 = plt.subplots(figsize=(10,4))
df_vac.plot(kind="bar", ax=ax3)
ax3.set_ylabel("Cobertura promedio (%)")
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
    df_ca["Schooling"],
    df_ca["Life expectancy"],
    c=df_ca["Income composition of resources"],
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
corr = df_ca[cols].corr()
fig5, ax5 = plt.subplots(figsize=(10,6))
sns.heatmap(corr, cmap="viridis", annot=False)
st.pyplot(fig5)

st.divider()

# ----------------------------------------------------
# TABLA CON FILTRO POR PAÍS
# ----------------------------------------------------
st.subheader("📂 Datos detallados por país")
st.dataframe(df_display)

st.divider()

# ----------------------------------------------------
# CONCLUSIÓN FINAL
# ----------------------------------------------------
st.subheader("📌 Conclusión final")
st.markdown(f"""
<div style="padding:20px; border-radius:12px; background:#B8D39D;">
<h3>✔ Costa Rica tiene mayor esperanza de vida porque:</h3>
– Mejores programas de vacunación (Hepatitis B: {avg_vac['Hepatitis B']['Costa Rica']:.1f}% vs {avg_vac['Hepatitis B']['Panama']:.1f}%)  
– Mayores niveles de educación  
– Índice social más fuerte  
– Modelo de salud más preventivo  

<h3>❌ Lo que NO explica la diferencia:</h3>
– GDP (${avg_gdp['Costa Rica']:.2f} vs ${avg_gdp['Panama']:.2f})  
– Crecimiento poblacional  

<h2><b>➡ Conclusión: educación + salud preventiva = mayor esperanza de vida.</b></h2>
</div>
""", unsafe_allow_html=True)
