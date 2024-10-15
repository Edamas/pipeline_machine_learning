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

# Função para gerar gráfico de scatterplot com linha de regressão
def grafico_scatterplot(dataframe, coluna_x, coluna_y, titulo="Scatterplot de Correlação", key=None):
    if coluna_x not in dataframe.columns or coluna_y not in dataframe.columns:
        raise KeyError(
            f"Colunas '{coluna_x}' e/ou '{coluna_y}' não foram encontradas no DataFrame.\n"
            f"Colunas disponíveis: {dataframe.columns.tolist()}")

    x = dataframe[coluna_x].dropna().values.reshape(-1, 1)
    y = dataframe[coluna_y].dropna().values.reshape(-1, 1)

    # Ajuste da regressão linear
    reg = LinearRegression().fit(x, y)
    y_pred = reg.predict(x).flatten()
    r2 = reg.score(x, y)

    # Definir os limites dos eixos com base nos valores dos pontos
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()

    # Opções do gráfico
    options = {
        "title": {"text": titulo, "left": "center"},
        "xAxis": {
            "type": "value",
            "name": coluna_x,
            "min": x_min,
            "max": x_max,
            "nameLocation": "middle",
            "nameGap": 25
        },
        "yAxis": {
            "type": "value",
            "name": coluna_y,
            "min": y_min,
            "max": y_max,
            "nameLocation": "middle",
            "nameRotate": 90,
            "nameGap": 50
        },
        "series": [
            {
                "type": "scatter",
                "name": "Pontos",
                "data": [[float(x[i][0]), float(y[i][0])] for i in range(len(x))],
                "symbolSize": 5,
                "emphasis": {"focus": "series"},
                "tooltip": {
                    "formatter": "function(params) { return '(' + params.value[0].toFixed(4) + ', ' + params.value[1].toFixed(4) + ')'; }"
                },
            },
            {
                "type": "line",
                "name": "Linha de Regressão",
                "data": [[float(x_min), float(reg.predict([[x_min]])[0][0])], [float(x_max), float(reg.predict([[x_max]])[0][0])]],
                "lineStyle": {"type": "solid", "color": "red", "width": 1},
                "label": {
                    "show": True,
                    "formatter": f"y = {reg.coef_[0][0]:.4f}x + {reg.intercept_[0]:.4f}\nR² = {r2:.4f}",
                    "position": "end",
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
            "top": "middle",
            "itemGap": 10,
            "textStyle": {"overflow": "truncate", "width": 150}
        }
    }

    st_echarts(options=options, height="500px", key=key)