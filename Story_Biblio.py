import pandas as pd
import plotly.express as px

def clasificar_narrativa(texto):
    palabras_pro = ["bloqueo", "revolución", "patria", "díaz-canel", "imperialismo"]
    palabras_anti = ["corrupción", "ineficiencia", "protesta", "crisis"]
    contador_pro = sum(texto.lower().count(palabra) for palabra in palabras_pro)
    contador_anti = sum(texto.lower().count(palabra) for palabra in palabras_anti)
    return "PRO" if contador_pro > contador_anti else "ANTI" if contador_anti > contador_pro else "NEUTRO"

def picos_comentarios_por_fecha(df):
    if df.empty: return px.line()
    df_fechas = df[df['fecha_comentario'].notna()].copy()
    df_fechas['fecha'] = df_fechas['fecha_comentario'].dt.date
    conteo = df_fechas.groupby('fecha').size().reset_index(name='count')
    conteo = conteo[conteo['count'] > 0].sort_values('fecha')
    fig = px.line(conteo, x='fecha', y='count', title='Tendencia de Comentarios')
    fig.update_xaxes(rangeslider_visible=True)
    return fig

def noticias_mas_comentadas(df, top_n=5):
    if df.empty: return pd.DataFrame()
    df_agrupado = df.groupby('titulo_noticia').size().reset_index(name='total_comentarios')
    return df_agrupado.sort_values('total_comentarios', ascending=False).head(top_n)

def analizar_consignas_cubanas(df):
    consignas = {
        "PRO": [
            "Patria o Muerte", "Viva la Revolución", "Socialismo o Muerte",
            "Cuba sí, bloqueo no", "Yo soy Fidel"
        ],
        "ANTI": [
            "Abajo la dictadura", "No tenemos miedo", "Libertad para los presos políticos",
            "Cuba libre", "No más represión", "no mas apagones"
        ]
    }

    resultados = {
        "Consigna": [],
        "Afinidad": [],
        "Frecuencia": [],
        "Porcentaje": []
    }

    total_comentarios = len(df)
    for afinidad, frases in consignas.items():
        for frase in frases:
            count = df['contenido_comentario'].str.contains(frase, case=False, regex=False).sum()
            porcentaje = (count / total_comentarios) * 100 if total_comentarios > 0 else 0

            resultados["Consigna"].append(frase)
            resultados["Afinidad"].append(afinidad)
            resultados["Frecuencia"].append(count)
            resultados["Porcentaje"].append(round(porcentaje, 2))

    df_resultados = pd.DataFrame(resultados)

    resumen = {
        "Total comentarios analizados": total_comentarios,
        "Consignas PRO detectadas": df_resultados[df_resultados["Afinidad"] == "PRO"]["Frecuencia"].sum(),
        "Consignas ANTI detectadas": df_resultados[df_resultados["Afinidad"] == "ANTI"]["Frecuencia"].sum(),
        "Consigna más frecuente": df_resultados.loc[df_resultados["Frecuencia"].idxmax(), "Consigna"]
    }

    return df_resultados.sort_values("Frecuencia", ascending=False), resumen

def analizar_emociones(texto):
    positivas = ["apoyo", "excelente", "gracias", "fuerte", "vencer"]
    negativas = ["corrupción", "protesta", "crisis", "bloqueo", "injusto"]
    score = sum(texto.lower().count(p) for p in positivas) - sum(texto.lower().count(n) for n in negativas)
    return ("positivo", 1) if score > 0 else ("negativo", 1) if score < 0 else ("neutral", 0)

def analisis_temporal(df):
    df['fecha'] = df['fecha_comentario'].dt.date
    actividad = df.groupby('fecha').size().reset_index(name='conteo')
    q75 = actividad['conteo'].quantile(0.75)
    actividad['pico'] = actividad['conteo'] > q75 * 1.5
    return actividad