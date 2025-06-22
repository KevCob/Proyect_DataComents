import plotly.express as px
import pandas as pd
from collections import Counter
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
    df['contenido_comentario'] = df['contenido_comentario'].fillna("")

    sentimientos = []
    for comentario in df['contenido_comentario']:
        if comentario.strip() == "":  
            sentimientos.append(0.0)  
        else:
            blob = TextBlob(comentario)  
            sentimientos.append(blob.sentiment.polarity)
    
    df['sentimiento'] = sentimientos  
    categorias = []
    for valor in df['sentimiento']:
        if valor > 0:
            categorias.append("Positivo")
        elif valor < 0:
            categorias.append("Negativo")
        else:
            categorias.append("Neutral")
    
    df['sentimiento_categoria'] = categorias  
    
    fig = px.pie(df, names='sentimiento_categoria', title='Distribución de Sentimientos')
    return fig

def generar_nube_palabras(df):
    palabras_excluidas = {
        'yo', 'tú', 'él', 'ella', 'nosotros', 'vosotros', 'ellos', 'ellas', 'usted', 'ustedes',
        'mi', 'tu', 'su', 'nuestro', 'vuestro', 'su', 'mío', 'tuyo', 'suyo',
        'que', 'cual', 'quien', 'cuyo', 'cuanto', 'donde', 'cuando', 'como',
        'y', 'o', 'pero', 'ni', 'que', 'si', 'aunque', 'porque', 'como',
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
        'a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'en', 'entre', 
        'hacia', 'hasta', 'para', 'por', 'según', 'sin', 'so', 'sobre', 'tras',
        'aquí', 'allí', 'ahora', 'antes', 'después', 'hoy', 'mañana', 'ayer', 
        'siempre', 'nunca', 'tarde', 'pronto', 'bien', 'mal', 'mejor', 'peor',
        'muy', 'mucho', 'poco', 'bastante', 'demasiado', 'casi', 'todo', 'nada', 'porque','también','además'
    }
    
    texto = ' '.join(df['contenido_comentario'].dropna().astype(str))
    
    palabras_filtradas = [
        word.lower() for word in texto.split() 
        if len(word) > 5 and word.lower() not in palabras_excluidas
    ]
    texto_filtrado = ' '.join(palabras_filtradas)
    
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        min_word_length=6,
        stopwords=palabras_excluidas
    ).generate(texto_filtrado)
    
    fig = plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Nube de Palabras Relevantes')
    return fig

def analizar_violencia(df, palabras_violencia=None):
    if palabras_violencia is None:
        palabras_violencia = ['matar', 'asesinar', 'destruir', 'violencia', 'golpear', 'apuñalar', 'estrangular', 'torturar', 'quemar', 'violar', 'atacar']
    
    df['violencia'] = df['contenido_comentario'].str.lower().str.count('|'.join(palabras_violencia))
    df_violencia = df.groupby('categoria')['violencia'].sum().reset_index()
    
    fig = px.pie(
        df_violencia,
        names='categoria',
        values='violencia',
        title='Distribución de Lenguaje Violento por Categoría'
    )
    return fig

def identificar_comentarios_repetidos(df, top_n=5):
    df['contenido_lower'] = df['contenido_comentario'].str.lower()
 
    repetidos = df[df.duplicated('contenido_lower', keep=False)]
    
    top_comentarios = repetidos.groupby('contenido_lower').size().nlargest(top_n).reset_index()
    top_comentarios.columns = ['Comentario', 'Repeticiones']

    fig = px.bar(
        top_comentarios,
        x='Repeticiones',
        y='Comentario',
        orientation='h',
        title=f'Top {top_n} Comentarios Más Repetidos',
        labels={'Repeticiones': 'Número de repeticiones', 'Comentario': 'Texto del comentario'}
    )

    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig