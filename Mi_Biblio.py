import plotly.express as px
import pandas as pd
import plotly as st
from collections import Counter
from geotext import GeoText
from textblob import TextBlob
import matplotlib.pyplot as plt
from wordcloud import WordCloud


def plot_comentarios_por_categoria(df):
    conteo = df['categoria'].value_counts().reset_index()
    fig = px.bar(conteo, x='categoria', y='count', 
                 title='Comentarios por Categoría',
                 labels={'categoria': 'Categoría', 'count': 'Total Comentarios'})
    return fig

def plot_tendencia_temporal(df):
    df['fecha_comentario'] = pd.to_datetime(df['fecha_comentario'], errors='coerce')
    df_fecha = df.groupby(df['fecha_comentario'].dt.date).size().reset_index(name='count')
    fig = px.line(df_fecha, x='fecha_comentario', y='count',
                  title='Tendencia de Comentarios',
                  labels={'fecha_comentario': 'Fecha', 'count': 'Comentarios'})
    return fig

def plot_top_noticias(df, top_n=10):
    top_noticias = df['titulo_noticia'].value_counts().head(top_n).reset_index()
    top_noticias.columns = ['titulo_noticia', 'total_comentarios']
    
    fig = px.bar(
        top_noticias,
        x='total_comentarios',
        y='titulo_noticia',
        orientation='h',
        title=f'Top {top_n} Noticias con Más Comentarios',
        labels={
            'titulo_noticia': 'Título de la Noticia',
            'total_comentarios': 'Número de Comentarios'
        }
    )
    
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    
    return fig

def plot_comentarios_por_dia(df):
    df['dia_semana'] = pd.to_datetime(df['fecha_comentario']).dt.day_name(locale='es')
    orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    conteo = df['dia_semana'].value_counts().reindex(orden_dias).reset_index()
    
    fig = px.bar(conteo, 
                 x='dia_semana', 
                 y='count',
                 title='Comentarios por Día de la Semana')
    return fig

def plot_radar_emociones(df):
    emociones = ['alegria', 'tristeza', 'enojo', 'sorpresa', 'miedo']
    conteo = [df['contenido_comentario'].str.contains(e, case=False).sum() for e in emociones]  
    fig = px.line_polar(r=conteo, theta=emociones, line_close=True, title='Distribución de Emociones')
    return fig  

def evolucion_palabras_clave(df, palabras):
    df['fecha'] = pd.to_datetime(df['fecha_comentario'])
    for palabra in palabras:
        df[palabra] = df['contenido_comentario'].str.contains(palabra, case=False)
    fig = px.line(df.groupby(df['fecha'].dt.date)[palabras].sum(), title='Evolución de Términos Clave')
    return fig



def analizar_sentimiento(df):
    # Paso 1: Limpiar datos (reemplazar NaN o None con strings vacíos)
    df['contenido_comentario'] = df['contenido_comentario'].fillna("")
    
    # Paso 2: Calcular sentimiento para cada comentario
    sentimientos = []
    for comentario in df['contenido_comentario']:
        if comentario.strip() == "":  # Si el comentario está vacío
            sentimientos.append(0.0)  # Sentimiento neutro
        else:
            blob = TextBlob(comentario)  # Analizar sentimiento
            sentimientos.append(blob.sentiment.polarity)
    
    df['sentimiento'] = sentimientos  # Añadir columna con resultados
    
    # Paso 3: Clasificar en categorías (Positivo, Neutral, Negativo)
    categorias = []
    for valor in df['sentimiento']:
        if valor > 0:
            categorias.append("Positivo")
        elif valor < 0:
            categorias.append("Negativo")
        else:
            categorias.append("Neutral")
    
    df['sentimiento_categoria'] = categorias  # Añadir columna de categorías
    
    fig = px.pie(df, names='sentimiento_categoria', title='Distribución de Sentimientos')
    return fig

def generar_nube_palabras(df):
    # Obtener todos los comentarios
    texto = ' '.join(df['contenido_comentario'].dropna())
    
    # Filtrar palabras con más de 5 caracteres
    palabras_filtradas = [word for word in texto.split() if len(word) > 5]
    texto_filtrado = ' '.join(palabras_filtradas)
    
    # Generar la nube de palabras
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        min_word_length=6  # Asegura que solo incluye palabras de 6+ caracteres
    ).generate(texto_filtrado)
    
    # Mostrar la nube
    fig = plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Nube de Palabras (palabras con 6+ caracteres)')
    return fig

def plot_longitud_comentarios(df):
    df['longitud'] = df['contenido_comentario'].str.len()
    fig = px.histogram(df, x='longitud', nbins=50, title='Distribución de Longitud de Comentarios')
    return fig