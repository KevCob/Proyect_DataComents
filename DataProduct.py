import streamlit as st
import Mi_Biblio as mb
import pandas as pd
import json
from datetime import datetime
from PIL import Image

st.set_page_config(
    page_title="EcoCubano | Análisis de Comentarios",
    page_icon="📢",
    layout="wide"
)

try:
    logo = Image.open('Logo.jpg')
    st.sidebar.image(logo, use_container_width=True)
except FileNotFoundError:
    st.sidebar.warning("Logo no encontrado. Asegúrate de tener 'logo.png' en la misma carpeta.")

st.title("📢 EcoCubano: Análisis de Comentarios")

@st.cache_data
def cargar_datos():
    with open('comentarios_cubadebate.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    noticias = data["analisis_comentarios"]["comentarios"]
    datos_aplanados = []
    for noticia in noticias:
        for comentario in noticia["comentarios"]:
            datos_aplanados.append({
                "titulo_noticia": noticia["titulo_noticia"],
                "categoria": noticia["categoria"],
                "fecha_comentario": comentario.get("fecha", "Sin fecha"),
                "contenido_comentario": comentario.get("contenido", ""),
                "usuario": comentario.get("usuario", "Anónimo")  
            })
    return pd.DataFrame(datos_aplanados)

df = cargar_datos()

df['fecha_comentario'] = pd.to_datetime(df['fecha_comentario'], errors='coerce')
df['dia_semana'] = df['fecha_comentario'].dt.day_name(locale='es')
df['longitud'] = df['contenido_comentario'].str.len()

with st.sidebar:
    st.header("🔍 Filtros Avanzados")
    
    categorias = ['Todas'] + sorted(df['categoria'].unique().tolist())
    categoria = st.selectbox(
        "Categoría:",
        options=categorias,
        index=0
    )
    
    fecha_min = df['fecha_comentario'].min().date()
    fecha_max = df['fecha_comentario'].max().date()
    rango_fechas = st.date_input(
        "Rango de fechas:",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )
    
    palabras_clave = st.text_input(
        "Palabras clave (separadas por comas):",
        "cuba, gobierno, economía"
    )
    
    st.header("⚙️ Configuración")
    top_n = st.slider("Top noticias a mostrar:", 3, 10, 5)
    mostrar_nube = st.checkbox("Mostrar nube de palabras", True)
    mostrar_sentimiento = st.checkbox("Mostrar análisis de sentimiento", True)
df_filtrado = df.copy()

if categoria != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria]

if len(rango_fechas) == 2:
    df_filtrado = df_filtrado[
        (df_filtrado['fecha_comentario'].dt.date >= rango_fechas[0]) &
        (df_filtrado['fecha_comentario'].dt.date <= rango_fechas[1])
    ]

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 General", 
    "📈 Temporal", 
    "🏆 Destacados", 
    "🧠 Análisis de Texto"
])

with tab1:
    st.subheader(f"Resumen general ({len(df_filtrado)} comentarios)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            mb.plot_comentarios_por_categoria(df_filtrado),
            use_container_width=True
        )
    with col2:
        st.plotly_chart(
            mb.plot_top_noticias(df_filtrado, top_n),
            use_container_width=True
        )
    
    st.metric("Comentarios analizados", len(df_filtrado))
    st.metric("Usuarios únicos", df_filtrado['usuario'].nunique())
    st.metric("Noticias diferentes", df_filtrado['titulo_noticia'].nunique())

with tab2:
    st.subheader("Análisis temporal")
    
    st.plotly_chart(
        mb.plot_tendencia_temporal(df_filtrado),
        use_container_width=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            mb.plot_comentarios_por_dia(df_filtrado),
            use_container_width=True
        )
    with col2:
        st.plotly_chart(
            mb.plot_longitud_comentarios(df_filtrado),
            use_container_width=True
        )

with tab3:
    st.subheader("Contenido destacado")
    
    st.plotly_chart(
        mb.plot_radar_emociones(df_filtrado),
        use_container_width=True
    )
    
    st.plotly_chart(
        mb.evolucion_palabras_clave(
            df_filtrado, 
            [p.strip() for p in palabras_clave.split(",")]
        ),
        use_container_width=True
    )

with tab4:
    st.subheader("Análisis de texto")
    
    if mostrar_sentimiento:
        st.plotly_chart(
            mb.analizar_sentimiento(df_filtrado),
            use_container_width=True
        )
    
    if mostrar_nube:
        st.pyplot(
            mb.generar_nube_palabras(df_filtrado),
            use_container_width=True
        )