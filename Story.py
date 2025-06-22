import json
import streamlit as st
import plotly.express as px
import Story_Biblio as sb 
import pandas as pd
from datetime import datetime

def cargar_datos(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        if "analisis_comentarios" not in data or "comentarios" not in data["analisis_comentarios"]:
            st.error("Estructura del JSON inválida")
            return pd.DataFrame()
        
        noticias = data["analisis_comentarios"]["comentarios"]
        datos = []
        
        for noticia in noticias:
            if "comentarios" not in noticia:
                continue
                
            if noticia.get("categoria", "").lower() == "politica":
                for comentario in noticia.get("comentarios", []):
                    contenido = comentario.get("contenido")
                    if contenido is None or not isinstance(contenido, str): 
                        contenido = ""  
                    
                    fecha_str = comentario.get("fecha", "")
                    if not fecha_str:
                        continue
                    
                    try:
                        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                    except ValueError:
                        continue
                    
                    datos.append({
                        "titulo_noticia": noticia.get("titulo_noticia", "Sin título"),
                        "fecha_comentario": fecha,
                        "contenido_comentario": contenido,  
                        "usuario": comentario.get("autor", "Anónimo")
                    })
        
        df = pd.DataFrame(datos)
        
        if not df.empty:
            df = df.sort_values('fecha_comentario')
            
        return df
    
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()

def mostrar_storytelling(df):
    df['narrativa'] = df['contenido_comentario'].apply(sb.clasificar_narrativa)
    df['emocion'], _ = zip(*df['contenido_comentario'].apply(sb.analizar_emociones))
    consignas_df, resumen_consignas = sb.analizar_consignas_cubanas(df)
    noticias_destacadas = sb.noticias_mas_comentadas(df, top_n=5)
    actividad_temporal = sb.analisis_temporal(df)
    
    st.markdown(f"""
    ## Dos años en los comentarios polìticos de Cubadebate
    *Un análisis de la participación digital a través de los ojos de una universitario*

    ---

    _En un contexto marcado por la transformación acelerada del ecosistema comunicativo cubano, 
    Con el creciente protagonismo de las redes sociales y la multiplicación de espacios informativos alternativos,
    el sitio Cubadebate sigue siendo uno de los principales nodos de participación digital en el país_
    _"A través de sus secciones de comentarios, miles de usuarios interactúan, opinan, confrontan y canalizan emociones frente a los temas de la agenda pública nacional."_

    Este estudio analiza {len(df)} comentarios políticos entre {df['fecha_comentario'].dt.date.min()} y {df['fecha_comentario'].dt.date.max()}, 
    como parte de una investigación universitaria sobre comunicación digital en Cuba.

    José Martínez, estudiante de cuarto año de Derecho en la Universidad de La Habana, llevaba tres años como presidente de la Federación Estudiantil Universitaria (FEU). 
    Su carisma y habilidad para mediar entre estudiantes y administración lo habían convertido en una figura respetada, pero él soñaba con  entrar en la política nacional.

    Una tarde, mientras revisaba las noticias en Cubadebate, notó algo peculiar: 
    los comentarios de una publicacìon superaban los 500 en solo unas horas. "¿Què genera tanta pasión?", se preguntó. Decidió investigar.


    """)

    st.plotly_chart(sb.picos_comentarios_por_fecha(df), use_container_width=True)
    st.markdown("""
    ### 29 de julio: El día que rompió récords
    _"No podía creer lo que veía. 675 comentarios en un solo día , pero , que tema será el que provocó tanta controversia en esta página.  
    ¿Será que el tema toca fibra sensibles de nuestra realidad cotidiana?"_

    **Dato clave**: El pico histórico del 29/07 superó en 3 veces el promedio diario
    -
    """)

    st.markdown("""
    ---

    ### Neutralidad aparente
    Al analizar los comentarios, José notó que el 88% eran neutrales: frases como "ponle corazòn" o "unidad del pueblo" dominaban el espacio. Pero en lugar de ver apatía, 
    él detectó miedo. "La gente no es indiferente -explicaba en una reunión de la FEU-, solo que no saben desde que perspectiva hablar"
    
    _"La clasificación de los comentarios políticos se pueden identificar en tres categorías principales (progobierno, críticos o neutros)"_
    """)
    
    fig_narrativa = px.pie(df, names='narrativa', title='Distribución de narrativas',
                          color_discrete_map={'NEUTRO':'gray', 'PRO':'blue', 'ANTI':'red'})
    st.plotly_chart(fig_narrativa, use_container_width=True)
    
    conteo_narrativas = df['narrativa'].value_counts().to_dict()
    st.markdown(f"""
    **Desglose académico**:
    - Neutrales: 88.5%  
    _(Ejemplo típico: "Interesante artículo, habrá que esperar los resultados")_
    - PRO: 9.27%  
    _(Ejemplo: "Esto demuestra los avances de nuestra Revolución")_
    - ANTI: 2.25%  
    _(Ejemplo: "Ojalá se cumpla lo prometido esta vez")_

    """)

    st.markdown("""
    ---

    ### Consignas vs. conversación
    "Hoy encontré algo curioso: 'Patria o Muerte' aparece 131 veces, 
    pero frases como 'No más apagones' ninguna. ¿Dónde quedaron las que vemos en Facebook?"

    **Hallazgo documentado**: Las consignas tradicionales predominan 34:1 sobre las críticas
    """)
  
    top_consignas = consignas_df[consignas_df['Frecuencia']>0].sort_values('Frecuencia', ascending=False)
    fig_consignas = px.bar(top_consignas, 
                          x='Consigna', y='Frecuencia', 
                          color='Afinidad',
                          color_discrete_map={'PRO':'blue', 'ANTI':'red'},
                          title='Consignas detectadas (frecuencia > 0)')
    st.plotly_chart(fig_consignas, use_container_width=True)
    
    st.markdown("""
    **Análisis comparativo**:
    - "Cuba Libre" (69 usos):  
    _Aparece tanto en contextos patrióticos como críticos_
    - "No tenemos miedo" (2 usos):  
    _Mínima presencia vs. su circulación en otras plataformas_
    - "Abajo la dictadura":  
    _Ausencia total en los datos analizados_

    _"Entonces esto refleja moderación de contenido, autocensura o diferencias demográficas entre plataformas'._
    _ Uno de los aspectos más novedosos de la investigación es el análisis léxico y discursivo de las consignas y frases que se repiten en los comentarios. _
    _¿Qué nivel de circulación tienen expresiones como “Patria o Muerte”, “Vamos con todo”, “Resistir y vencer”? _
    _¿Se utilizan como formas de afirmación política o como recursos de ironía o crítica?"_
    """)



    st.markdown("""
    ---
    ### Las noticias que generaron más debate
    _"Al analizar los artículos más comentados, emerge un patrón claro: los temas migratorios dominan la conversación"_
    """)

    noticias_destacadas = sb.noticias_mas_comentadas(df, top_n=5)

    if not noticias_destacadas.empty:
        st.dataframe(noticias_destacadas.style.highlight_max(axis=0), use_container_width=True)
        st.markdown(f"""
        **Análisis temático**:
        - La noticia más comentada (*{noticias_destacadas.iloc[0]['titulo_noticia']}*) acumuló {noticias_destacadas.iloc[0]['total_comentarios']} comentarios
       
        
        _"No es casualidad que los temas migratorios generen tanta interacción. Para muchos cubanos, 
        la migración no es solo un tema político, sino una experiencia personal o familiar que toca fibras sensibles. 
        Las discusiones reflejan tanto frustraciones cotidianas como debates ideológicos profundos sobre el futuro del país."_
        """)
    else:
        st.warning("No se encontraron datos de noticias destacadas")

    st.markdown("""
    ---

    ### Conclusiones
    _"Podemos determinar que los datos muestran patrones claros, pero detrás de ellos hay historias complejas:_

    1. **El silencio elocuente**: La neutralidad predominante contrasta con el debate más polarizado en otros espacios
    2. **Los temas sensibles**: Migración moviliza más que política partidista
    3. **Las palabras ausentes**: Algunas frases comunes en la calle no encuentran eco aquí
                
    _Comprender las formas en que la ciudadanía cubana se expresa, debate y construye sentido colectivo en Cubadebate, 
    resulta decisivo en una realidad donde la participación digital es cada vez más relevante. 
    Al mapear emociones, temas, patrones discursivos y niveles de participación,  no solo  ofrecemos una lectura más precisa del ECO ciudadano en línea, 
    sino también ofrecemos  herramientas que contribuyan a fortalecer un diálogo público más inclusivo, informado y constructivo._
                    
    Cuando José se graduó, dejó instalado en la FEU un grupo que analiza sistemáticamente las redes sociales para detectar problemas emergentes. 
    Su lema, inspirado en sus años de investigación, resume su filosofía:

    "La verdad no está ni solo en los discursos oficiales ni solo en las críticas destructivas. 
    Está en lo que la gente dice cuando cree que nadie la escucha. Nuestro trabajo es oír esos susurros y convertirlos en acciones".

    """)

st.set_page_config(page_title="Cubadebate Analytics", page_icon="📊", layout="wide")

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

try:
    df = cargar_datos("comentarios_cubadebate.json")
    if df.empty:
        st.warning("No se encontraron datos para analizar. Por favor sube un archivo válido.")
    else:
        mostrar_storytelling(df)
except Exception as e:
    st.error(f"Error en la aplicación: {str(e)}")