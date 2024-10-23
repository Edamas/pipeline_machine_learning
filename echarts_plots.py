import streamlit as st
from streamlit_echarts import st_echarts
from sklearn.linear_model import LinearRegression

# Função para gerar gráfico de barras
def grafico_barras(dataframe, colunas, titulo="Gráfico de Barras", key=None):
    if isinstance(colunas, str):
        colunas = [colunas]
    
    colunas_existentes = [col for col in colunas if col in dataframe.columns]
    
    if not colunas_existentes:
        raise KeyError(f"Nenhuma das colunas especificadas foi encontrada no DataFrame.\n"
                       f"Colunas solicitadas: {colunas}\n"
                       f"Colunas disponíveis: {dataframe.columns.tolist()}")

    data = []
    for coluna in colunas_existentes:
        data.append({"name": coluna, "type": "bar", "data": dataframe[coluna].dropna().tolist()})

    labels = dataframe.index.strftime('%d/%m/%Y').tolist()

    options = {
        "title": {"text": titulo, "left": "center"},
        "xAxis": {
            "type": "category",
            "data": labels,
            "name": "Data",
            "nameLocation": "middle",
            "nameGap": 25
        },
        "yAxis": {
            "type": "value",
            "name": "Valores",
            "nameLocation": "middle",
            "nameRotate": 90,
            "nameGap": 50
        },
        "series": data,
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"}
        },
        "toolbox": {"feature": {"saveAsImage": {}}},
        "legend": {
            "show": True,
            "orient": "top",
            "right": "-5%",
            "top": "middle",
            "itemGap": 10,
            "textStyle": {"overflow": "truncate", "width": 150}
        }
    }

    st_echarts(options=options, height="500px", key=key)

# Função para gerar gráfico de linhas
def grafico_linhas(dataframe, colunas, titulo="Gráfico de Linhas", key=None):
    if isinstance(colunas, str):
        colunas = [colunas]
    
    
    colunas_existentes = [col for col in colunas if col in dataframe.columns]
    
    if not colunas_existentes:
        raise KeyError(
            f"Nenhuma das colunas especificadas foi encontrada no DataFrame.\n"
            f"Colunas solicitadas: {colunas}\n"
            f"Colunas disponíveis: {dataframe.columns.tolist()}")

    data = []
    for coluna in colunas_existentes:
        data.append({"name": coluna, "type": "line", "data": dataframe[coluna].dropna().tolist()})

    labels = dataframe.index.strftime('%d/%m/%Y').tolist()
    
    
    options = {
        "title": {"text": titulo, "left": "center"},
        "xAxis": {
            "type": "category",
            "data": labels,
            "name": "Data",
            "nameLocation": "middle",
            "nameGap": 25
        },
        "yAxis": {
            "type": "value",
            "name": "Valores",
            "nameLocation": "middle",
            "nameRotate": 90,
            "nameGap": 50
        },
        "series": data,
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "cross"}
        },
        "toolbox": {"feature": {"saveAsImage": {}}},
        "legend": {
            "show": True,
            "orient": "top",
            "right": "-5%",
            "top": "middle",
            "itemGap": 10,
            "textStyle": {"overflow": "truncate", "width": 150}
        }
    }

    st_echarts(options=options, height="500px", key=key)



def grafico_scatterplot(dataframe, coluna_x, coluna_y, titulo="Gráfico de Dispersão", x_min_plot=None, x_max_plot=None, y_min_plot=None, y_max_plot=None, reg=None, r2=None, valor_x=None, valor_y_previsto=None, key=None):
    pass
def grafico_scatterplot(
                    dataframe,
                    coluna_x,
                    coluna_y,
                    titulo,
                    key,
                    x_min_plot,
                    x_max_plot,
                    y_min_plot,
                    y_max_plot,
                    reg,
                    ponto_selecionado,
                    valor_x,
                    valor_y_previsto,
                ):
    # Opções do gráfico
    x = dataframe[coluna_x].values.reshape(-1, 1).tolist()
    y = dataframe[coluna_y].values.reshape(-1, 1).tolist()

    r2 = reg.score(x, y)
    scatter_data = dataframe.values.tolist()
    regression_data = [[float(x_min_plot), float(reg.predict([[x_min_plot]])[0][0])], [float(x_max_plot), float(reg.predict([[x_max_plot]])[0][0])]]
    options = {
        "title": {"text": titulo, "left": "center"},
        "xAxis": {
            "type": "value",
            "name": coluna_x,
            "min": float(x_min_plot),
            "max": float(x_max_plot),
            "nameLocation": "middle",
            "nameGap": 35
        },
        "yAxis": {
            "type": "value",
            "name": coluna_y,
            "min": float(y_min_plot),
            "max": float(y_max_plot),
            "nameLocation": "middle",
            "nameRotate": 90,
            "nameGap": 50
        },
        "series": [
            {
                "type": "scatter",
                "name": "Pontos",
                "data": scatter_data,
                "symbolSize": 5,
                "itemStyle": {"opacity": 0.75},
                "emphasis": {"focus": "series"},
                "tooltip": {
                    "formatter": "function(params) { return '(' + params.value[0].toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ', ' + params.value[1].toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ')'; }"
                },
            },
            {
                "type": "line",
                "name": "Linha de Regressão",
                "data": regression_data,
                "lineStyle": {"type": "solid", "color": "green", "width": 1},
                "label": {
                    "show": True,
                    "formatter": f"y = {reg.coef_[0][0]:.4f}x + {reg.intercept_[0]:.4f}\nR² = {r2:.4f}",
                    "position": "end",
                },
            },
            {
                "type": "scatter",
                "name": "Ponto Selecionado",
                "data": [[valor_x, valor_y_previsto[0]]] if valor_x is not None and valor_y_previsto is not None else [],
                "symbolSize": 20,
                "itemStyle": {"color": "red", "opacity": 0.75},
                "label": {
                    "show": True,
                    "position": "top",
                },
            }
        ],
        "tooltip": {
            "trigger": "item",
        },
        "toolbox": {"feature": {"saveAsImage": {}}},
        "legend": {
            "show": True,
            "orient": "top",
            "right": "-5%",
            "top": "4%",
            "itemGap": 10,
            "textStyle": {"overflow": "truncate", "width": 150}
        }
    }

    # Gráfico
    st_echarts(options=options, height="500px", key=f"echarts_{key}_{coluna_x}_{coluna_y}")
