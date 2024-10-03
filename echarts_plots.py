from streamlit_echarts import st_echarts
import pandas as pd
import streamlit as st

# Função para gerar gráfico de barras
def grafico_barras(dataframe, valor_coluna, key=None):
    # Verifique se o índice é datetime e converta para string formatada
    if pd.api.types.is_datetime64_any_dtype(dataframe.index):
        labels = dataframe.index.strftime('%d/%m/%Y').tolist()  # Converte para formato dd/mm/aaaa
    else:
        st.error("O índice não está em formato datetime.")
        return  # Sai da função se o índice não for datetime

    # Converte a coluna de valores para uma lista
    valores = dataframe[valor_coluna].tolist()

    # Prepare os dados para o gráfico
    options = {
        "xAxis": {"type": "category", "data": labels},  # Labels já são strings formatadas
        "yAxis": {"type": "value"},
        "series": [{"data": valores, "type": "bar"}],
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "title": {"text": "Gráfico de Barras", "left": "center"},
        "toolbox": {"feature": {"saveAsImage": {}}},
    }

    # Tente renderizar o gráfico, lidando com possíveis erros
    try:
        st_echarts(options=options, height="500px", key=key)
    except Exception as e:
        st.error(f"Erro ao renderizar gráfico: {e}")


# Função para gerar gráfico de linhas
def grafico_linhas(dataframe, valor_coluna):
    if not pd.api.types.is_datetime64_any_dtype(dataframe.index):
        dataframe.index = pd.to_datetime(dataframe.index)

    labels = dataframe.index.strftime('%d/%m/%Y').tolist()
    valores = dataframe[valor_coluna].tolist()

    options = {
        "xAxis": {"type": "category", "data": labels},
        "yAxis": {"type": "value"},
        "series": [{"data": valores, "type": "line"}],
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
        "title": {"text": "Gráfico de Linhas", "left": "center"},
        "toolbox": {"feature": {"saveAsImage": {}}},
    }
    st_echarts(options=options, height="500px")


# Função para gerar scatterplot
def grafico_scatterplot(dataframe, valor_coluna):
    labels = dataframe.index.tolist()
    valores = dataframe[valor_coluna].tolist()

    options = {
        "xAxis": {"type": "category", "data": labels},
        "yAxis": {"type": "value"},
        "series": [{"data": valores, "type": "scatter"}],
        "tooltip": {"trigger": "item"},
        "title": {"text": "Scatterplot", "left": "center"},
        "toolbox": {"feature": {"saveAsImage": {}}},
    }
    st_echarts(options=options, height="500px")


# Função para gerar gráfico de candlestick
def grafico_candlestick(dataframe, open_col, close_col, low_col, high_col):
    labels = dataframe.index.tolist()
    dados_candlestick = [
        [dataframe[open_col][i], dataframe[close_col][i], dataframe[low_col][i], dataframe[high_col][i]]
        for i in range(len(dataframe))
    ]

    options = {
        "xAxis": {"type": "category", "data": labels},
        "yAxis": {"type": "value"},
        "series": [{"data": dados_candlestick, "type": "candlestick"}],
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
        "title": {"text": "Gráfico Candlestick", "left": "center"},
        "toolbox": {"feature": {"saveAsImage": {}}},
    }
    st_echarts(options=options, height="500px")


# Função para gerar violin plot
def grafico_violin(dataframe, valor_coluna):
    valores = dataframe[valor_coluna].tolist()

    options = {
        "xAxis": {"type": "category", "data": ["Distribuição"]},
        "yAxis": {"type": "value"},
        "series": [
            {
                "data": valores,
                "type": "boxplot",
                "boxWidth": [7, 50],  # Violin width
                "tooltip": {"formatter": "{b}: {c}"},
            }
        ],
        "title": {"text": "Violin Plot", "left": "center"},
        "tooltip": {"trigger": "item"},
        "toolbox": {"feature": {"saveAsImage": {}}},
    }
    st_echarts(options=options, height="500px")
