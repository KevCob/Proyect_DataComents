import json
import streamlit as st
from Storie_Biblio import (
    clasificar_narrativa,
    picos_comentarios_por_fecha,
    noticias_mas_comentadas,
    detectar_consignas,
    analizar_dias_clave,
    asignar_roles_noticias,
    generar_tuit_definitivo
)
import pandas as pd
from datetime import datetime

def cargar_datos(ruta_archivo):
    """
    Carga y procesa los datos del archivo JSON
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Validar estructura del JSON
        if "analisis_comentarios" not in data or "comentarios" not in data["analisis_comentarios"]:
            st.error("Estructura del JSON inválida")
            return pd.DataFrame()
        
        noticias = data["analisis_comentarios"]["comentarios"]
        datos = []
        
        for noticia in noticias:
            if "comentarios" not in noticia:
                continue
                
            if noticia.get("categoria", "").lower() == "politica":
                for comentario in noticia["comentarios"]:
                    try:
                        fecha = datetime.strptime(comentario.get("fecha", ""), "%Y-%m-%d")
                    except:
                        continue  # Saltar comentarios sin fecha válida
                    
                    datos.append({
                        "titulo_noticia": noticia.get("titulo_noticia", "Sin título"),
                        "fecha_comentario": fecha,
                        "contenido_comentario": comentario.get("contenido", ""),
                        "usuario": comentario.get("autor", "Anónimo"),
                        "contenido": f"{noticia.get('titulo_noticia', '')} {comentario.get('contenido', '')}"
                    })
        
        return pd.DataFrame(datos)
    
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()

def mostrar_panel_principal(df):
    """
    Muestra el panel principal con todas las visualizaciones
    """
    # Header con métricas
    st.header("📊 Panel de Análisis de Comentarios Políticos")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Comentarios", len(df))
    col2.metric("Período Analizado", 
               f"{df['fecha_comentario'].min().strftime('%d/%m/%Y')} - {df['fecha_comentario'].max().strftime('%d/%m/%Y')}")
    col3.metric("Noticias Analizadas", df['titulo_noticia'].nunique())
    
    st.divider()
    
    # Sección 1: Evolución temporal de comentarios
    st.header("📈 Evolución Temporal de Comentarios")
    st.plotly_chart(picos_comentarios_por_fecha(df), use_container_width=True)
    
    # Sección 2: Análisis de días clave
    st.header("🗓️ Días Clave y Narrativa Dominante")
    dias_clave = analizar_dias_clave(df)
    st.dataframe(dias_clave.head(10), use_container_width=True)
    
    # Sección 3: Noticias más comentadas
    st.header("📰 Noticias Más Comentadas")
    noticias_destacadas = noticias_mas_comentadas(df, top_n=8)
    if not noticias_destacadas.empty:
        st.dataframe(noticias_destacadas, use_container_width=True)
    else:
        st.warning("No se encontraron noticias destacadas")
    
    # Sección 4: Roles de las noticias
    st.header("🦸 Roles de las Noticias")
    roles_noticias = asignar_roles_noticias(df)
    st.dataframe(roles_noticias.head(10), use_container_width=True)
    
    # Sección 5: Ejemplo de tweet definitivo
    if not noticias_destacadas.empty:
        st.header("💬 Tweet Definitivo de Noticia Destacada")
        noticia_ejemplo = noticias_destacadas.iloc[0]['titulo_noticia']
        tuit = generar_tuit_definitivo(df, noticia_ejemplo)
        st.markdown(tuit)
    
    # Sección 6: Detección de consignas
    st.header("🔍 Detección de Consignas Políticas")
    comentarios_con_consignas = df[df['contenido_comentario'].apply(detectar_consignas)]
    st.metric("Comentarios con consignas", len(comentarios_con_consignas))
    if len(comentarios_con_consignas) > 0:
        st.dataframe(comentarios_con_consignas[['usuario', 'contenido_comentario']].head(10), use_container_width=True)

# Configuración de la aplicación
st.set_page_config(
    page_title="Analizador de Narrativas Políticas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar con configuración
with st.sidebar:
    st.title("Configuración")
    archivo = st.file_uploader("Subir archivo JSON", type=["json"])
    if archivo:
        try:
            datos = json.load(archivo)
            with open("comentarios_cubadebate.json", "w", encoding="utf-8") as f:
                json.dump(datos, f)
            st.success("Archivo cargado correctamente")
        except Exception as e:
            st.error(f"Error al procesar archivo: {str(e)}")

# Carga y visualización de datos
try:
    df = cargar_datos("comentarios_cubadebate.json")
    
    if df.empty:
        st.warning("No se encontraron datos para analizar. Por favor sube un archivo válido.")
    else:
        mostrar_panel_principal(df)

except Exception as e:
    st.error(f"Error en la aplicación: {str(e)}")
    st.error("Por favor verifica que el archivo JSON tenga la estructura correcta.")