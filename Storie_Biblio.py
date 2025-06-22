import pandas as pd
import plotly.express as px
from collections import defaultdict, Counter

def clasificar_narrativa(texto):
    """
    Clasifica el texto en: PRO (pro-gobierno), ANTI (crítico) o NEUTRO
    Versión sin lambda, con umbral ajustable
    """
    palabras_pro = ["bloqueo", "revolución", "patria", "díaz-canel", "imperialismo"]
    palabras_anti = ["corrupción", "ineficiencia", "protesta", "crisis"]
    
    contador_pro = 0
    contador_anti = 0
    texto = texto.lower()
    
    for palabra in palabras_pro:
        contador_pro += texto.count(palabra)
    
    for palabra in palabras_anti:
        contador_anti += texto.count(palabra)
    
    if contador_pro > contador_anti:
        return "PRO"
    elif contador_anti > contador_pro:
        return "ANTI"
    else:
        return "NEUTRO"



def picos_comentarios_por_fecha(df):
    if df.empty:
        return px.line()  # Gráfico vacío si no hay datos
    
    # Asegurarnos de que solo usamos fechas válidas
    df_fechas_validas = df[df['fecha_comentario'].notna()].copy()
    
    # Convertir a fecha (sin hora)
    df_fechas_validas['fecha'] = df_fechas_validas['fecha_comentario'].dt.date
    
    # Agrupar por fecha válida
    conteo_fechas = df_fechas_validas.groupby('fecha').size().reset_index(name='count')
    
    # Ordenar por fecha para mejor visualización
    conteo_fechas = conteo_fechas.sort_values('fecha')
    
    # Filtrar solo fechas con comentarios (evitar días con 0)
    conteo_fechas = conteo_fechas[conteo_fechas['count'] > 0]
    
    fig = px.line(
        conteo_fechas,
        x='fecha',
        y='count',
        title='📅 Tendencia Diaria de Comentarios Políticos',
        labels={'fecha': 'Fecha', 'count': 'Comentarios'},
        markers=True
    )
    fig.update_xaxes(
        rangeslider_visible=True,
        range=[conteo_fechas['fecha'].min(), conteo_fechas['fecha'].max()]
    )
    return fig

def noticias_mas_comentadas(df, top_n=5):
    if df.empty:
        return pd.DataFrame()
    
    try:
        df_agrupado = df.groupby(['titulo_noticia']).agg(
            fecha_publicacion=('fecha_comentario', 'min'),
            total_comentarios=('titulo_noticia', 'size')
        ).reset_index()
        
        df_top = df_agrupado.sort_values('total_comentarios', ascending=False).head(top_n)
        df_top['fecha_publicacion'] = df_top['fecha_publicacion'].dt.strftime('%Y-%m-%d')
        return df_top[['titulo_noticia', 'fecha_publicacion', 'total_comentarios']]
    except:
        return pd.DataFrame()
    

def detectar_consignas(texto):
    """
    Identifica frases de campaña o consignas políticas
    """
    consignas = [
        "venceremos",
        "patria o muerte",
        "no al bloqueo",
        "cuba vive",
        "unidos venceremos"
    ]
    return any(consigna in texto.lower() for consigna in consignas)

def analizar_dias_clave(df):
    """
    Identifica los días con más actividad y su narrativa dominante
    """
    # Paso 1: Extraer fecha sin hora
    df['fecha'] = df['fecha_comentario'].dt.date
    
    # Paso 2: Contar comentarios por día
    conteo_dias = df.groupby('fecha').size().reset_index(name='total_comentarios')
    
    # Paso 3: Determinar narrativa dominante por día
    narrativas_dominantes = []
    for fecha in conteo_dias['fecha']:
        comentarios_dia = df[df['fecha'] == fecha]['contenido_comentario']
        narrativas = [clasificar_narrativa(comentario) for comentario in comentarios_dia]
        narrativa_comun = max(set(narrativas), key=narrativas.count)
        narrativas_dominantes.append(narrativa_comun)
    
    conteo_dias['narrativa_dominante'] = narrativas_dominantes
    return conteo_dias.sort_values('total_comentarios', ascending=False)

def asignar_roles_noticias(df):
    """
    Clasifica las noticias en: Héroe (PRO), Villano (ANTI) o Anti-héroe (NEUTRO)
    """
    noticias_analizadas = []
    noticias_unicas = df['titulo_noticia'].unique()
    
    for noticia in noticias_unicas:
        comentarios = df[df['titulo_noticia'] == noticia]['contenido_comentario']
        narrativas = [clasificar_narrativa(comentario) for comentario in comentarios]
        
        # Determinar narrativa principal
        conteo_narrativas = {}
        for narrativa in narrativas:
            conteo_narrativas[narrativa] = conteo_narrativas.get(narrativa, 0) + 1
        
        narrativa_principal = max(conteo_narrativas, key=conteo_narrativas.get)
        
        # Asignar rol
        if narrativa_principal == "PRO":
            rol = "🦸 Héroe"
        elif narrativa_principal == "ANTI":
            rol = "👿 Villano"
        else:
            rol = "🃏 Anti-héroe"
        
        noticias_analizadas.append({
            'noticia': noticia,
            'total_comentarios': len(comentarios),
            'rol': rol
        })
    
    return pd.DataFrame(noticias_analizadas).sort_values('total_comentarios', ascending=False)

def generar_tuit_definitivo(df, titulo_noticia):
    """
    Crea un resumen estilo tweet de una noticia viral
    """
    datos_noticia = df[df['titulo_noticia'] == titulo_noticia]
    
    # Encontrar comentario más largo (como proxy al más relevante)
    comentario_top = ""
    max_longitud = 0
    for comentario in datos_noticia['contenido_comentario']:
        if len(str(comentario)) > max_longitud:
            max_longitud = len(str(comentario))
            comentario_top = comentario
    
    # Determinar narrativa dominante
    narrativas = [clasificar_narrativa(comentario) for comentario in datos_noticia['contenido_comentario']]
    narrativa_dominante = max(set(narrativas), key=narrativas.count)
    
    # Emoji correspondiente
    emoji = "🚩" if narrativa_dominante == "PRO" else "💢" if narrativa_dominante == "ANTI" else "➖"
    
    return f"""
    🗞️ **{titulo_noticia[:50]}...**
    💬 *"{str(comentario_top)[:100]}..."*
    🔥 **Narrativa dominante**: {narrativa_dominante} {emoji}
    📊 **Total comentarios**: {len(datos_noticia)}
    """