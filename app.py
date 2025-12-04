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
    page_icon="logo\logo.png",
    layout="wide",
)

# Tema visual suave
st.markdown("""
<style>
body {
    background-color: #f7fdfb;
}
.block-container {
    padding-top: 1rem;
}
h1, h2, h3 {
    color: #196f5c;
}
</style>
""", unsafe_allow_html=True)

plt.style.use("seaborn-v0_8-whitegrid")

# ----------------------------------------------------
# CARGA DE DATOS
# ----------------------------------------------------
@st.cache_data
def load_data(path="Life Expectancy Data.csv"):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# --- FILTRAR SOLO PANAMÁ Y COSTA RICA ---
countries = ["Costa Rica", "Panama"]


#Columnas a limpiar
cols = [
    "Year", "Life expectancy", "Adult Mortality", "infant deaths", "Alcohol",
    "percentage expenditure", "Hepatitis B", "Measles", "BMI", "under-five deaths",
    "Polio", "Total expenditure", "Diphtheria", "HIV/AIDS", "GDP", "Population",
    "thinness  1-19 years", "thinness 5-9 years",
    "Income composition of resources", "Schooling"
]

df_ca = df[df["Country"].isin(countries)].copy()
df_ca.columns = df_ca.columns.str.strip()

# Convertir y rellenar
for col in cols:
    df_ca[col] = pd.to_numeric(df_ca[col], errors="coerce")
    df_ca[col] = df_ca.groupby("Country")[col].transform(lambda x: x.fillna(x.mean()))

# ----------------------------------------------------
# TÍTULO PRINCIPAL
# ----------------------------------------------------
st.title("📊 Healthlytics Dashboard")
st.subheader("“¿Por qué Costa Rica tiene mayor esperanza de vida que Panamá?”")

st.write("""
         A través de este dashboard analizaremos los factores que explican por qué Costa Rica mantiene una esperanza de vida más alta que Panamá a lo largo del tiempo. Cada gráfica responde una parte de esta pregunta hasta llegar a una conclusión final basada en datos.
         """)

st.divider()

# ----------------------------------------------------
# GRÁFICA 1 - EL PROBLEMA
# ----------------------------------------------------
with st.container():
    st.subheader("📈 1. Tendencia de esperanza de vida")
    st.write("""
            La diferencia es clara: **Costa Rica supera constantemente a Panamá** en esperanza de vida
            """)
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
    <div style="padding:12px; border-radius:10px; background:#e3f8f1;">
    Costa Rica mantiene una ventaja constante sobre Panamá a través del tiempo.
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------
# GRÁFICA 2 - ECONOMÍA
# ----------------------------------------------------
with st.container():
    st.subheader("💰 2. ¿La economía explica la diferencia?")
    st.write("""
            Primero evaluamos si el **GDP** (nivel económico) podría justificar la diferencia en esperanza de vida
            """)

    df_gdp = df_ca.groupby("Country")["GDP"].mean().sort_values()

    fig2, ax2 = plt.subplots(figsize=(8,4))
    ax2.barh(df_gdp.index, df_gdp.values)
    ax2.set_xlabel("GDP Promedio")
    ax2.set_title("GPD promedio por país")

    st.pyplot(fig2)

    st.markdown("""
    <div style="padding:12px; border-radius:10px; background:#ffecea;">
    El GDP no explica la diferencia en esperanza de vida: Panamá incluso tiene niveles similares o mayores.
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------
# GRÁFICA 3 - SALUD PREVENTIVA
# ----------------------------------------------------
with st.container():
    st.subheader("💉 3. ¿Mejores programas de vacunación?")
    st.write("""
            La vacunación y la prevención influyen directamente en la longevidad.
            """)

    vac_cols = ["Hepatitis B", "Polio", "Diphtheria"]
    df_vac = df_ca.groupby("Country")[vac_cols].mean()

    fig3, ax3 = plt.subplots(figsize=(10,4))
    df_vac.plot(kind="bar", ax=ax3)
    ax3.set_ylabel("Cobertura promedio (%)")
    ax3.grid(alpha=0.3)

    st.pyplot(fig3)

    st.markdown("""
    <div style="padding:12px; border-radius:10px; background:#e3f8f1;">
    Costa Rica presenta mejores programas de vacunación, un factor clave para la longevidad.
    </div>
    """, unsafe_allow_html=True)
st.divider()

# ----------------------------------------------------
# GRÁFICA 4 - EDUCACIÓN
# ----------------------------------------------------
with st.container():
    st.subheader("🎓 4. Educación vs esperanza de vida")
    st.write("""
            La educación es uno de los predictores sociales más fuertes de salud y longevidad.
            """)

    fig4, ax4 = plt.subplots(figsize=(10,5))
    scatter = ax4.scatter(
        df_ca["Schooling"],
        df_ca["Life expectancy"],
        c=df_ca["Income composition of resources"],
        cmap= "viridis",
        s=80,
        alpha=0.8
    )

    ax4.set_xlabel("Año de escolaridad")
    ax4.set_ylabel("Esperanza de vida (años)")
    ax4.grid(alpha=0.3)

    plt.colorbar(scatter, label="Índice educativo / ingreso")
    st.pyplot(fig4)

    st.markdown("""
    <div style="padding:12px; border-radius:10px; background:#eaf3ff;">
    Costa Rica tiene mayor escolaridad y mejor índice social: esto sí impacta directamente la esperanza de vida.
    </div>
    """, unsafe_allow_html=True)
st.divider()

# ----------------------------------------------------
# GRÁFICA 5 - CORRELACIONES
# ----------------------------------------------------
with st.container():
    st.subheader("🔬 5. ¿Qué factores influyen más?")
    st.write("""
            Este mapa ayuda a identificar qué variables están más relacionadas con la esperanza de vida.
            """)
    corr = df_ca[cols].corr()

    fig5, ax5 = plt.subplots(figsize=(10,6))
    sns.heatmap(corr, cmap="viridis", annot=False)

    st.pyplot(fig5)


st.divider()


# ================================
#   CONCLUSIÓN FINAL
# ================================
st.subheader("📌 Conclusión final")

st.markdown("""
<div style="padding:20px; border-radius:12px; background:#d6f5e3;">
<h3>✔ Costa Rica tiene mayor esperanza de vida porque:</h3>
– Mejores programas de vacunación  
– Mayores niveles de educación  
– Índice social más fuerte  
– Modelo de salud más preventivo  

<h3>❌ Lo que NO explica la diferencia:</h3>
– GDP  
– Economía general  
– Crecimiento poblacional  

<h2><b>➡ Conclusión: educación + salud preventiva = mayor esperanza de vida.</b></h2>
</div>
""", unsafe_allow_html=True)
