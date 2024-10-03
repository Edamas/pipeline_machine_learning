import pandas as pd

def calcular_novas_colunas(df, calculo):
    if calculo == "Acumulado":
        df['acumulado'] = df['valor'].cumsum()
    elif calculo == "Variação Absoluta":
        df['variacao_absoluta'] = df['valor'].diff()
    elif calculo == "Variação Percentual":
        df['variacao_percentual'] = df['valor'].pct_change() * 100
    elif calculo == "Dia da Semana":
        df['dia_da_semana'] = df['data'].dt.dayofweek + 1
    elif calculo == "Número do Mês":
        df['numero_do_mes'] = df['data'].dt.month
    return df
