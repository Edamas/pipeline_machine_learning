import streamlit as st
from streamlit_echarts import st_echarts
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
import pandas as pd
import statsmodels.api as sm
import plotly.graph_objects as go
import scipy.stats as stats


def scatter_plot_with_regression(dataframe, x_column, y_column, title, normalize=False, key=None):
    import numpy as np
    from sklearn.linear_model import LinearRegression
    import statsmodels.api as sm
    from streamlit_echarts import st_echarts

    df = dataframe[[x_column, y_column]].dropna()
    if normalize:
        df = (df - df.min()) / (df.max() - df.min())

    # Ordena os dados pelo eixo x para garantir que a área de confiança seja contínua
    df = df.sort_values(by=x_column)

    x = df[x_column].values.reshape(-1, 1)
    y = df[y_column].values

    model = LinearRegression()
    model.fit(x, y)
    y_pred = model.predict(x)

    # Intervalo de confiança
    X_with_const = sm.add_constant(x)
    est = sm.OLS(y, X_with_const)
    est_fit = est.fit()
    predictions = est_fit.get_prediction(X_with_const)
    ci_low, ci_upp = predictions.conf_int().T

    scatter_data = [{'value': [float(x_val[0]), float(y_val)]} for x_val, y_val in zip(x, y)]
    regression_line = [{'value': [float(x_val[0]), float(y_val)]} for x_val, y_val in zip(x, y_pred)]
    
    # Área de confiança - criar polígono com as partes superior e inferior
    confidence_area = (
        [{'value': [float(x_val[0]), float(ci)]} for x_val, ci in zip(x, ci_low)] +
        [{'value': [float(x_val[0]), float(ci)]} for x_val, ci in zip(x[::-1], ci_upp[::-1])]
    )

    options = {
        'title': {'text': title},
        'tooltip': {'trigger': 'axis'},
        'legend': {
            'data': ['Pontos de Dados', 'Linha de Regressão', 'Área de Confiança'],
            'bottom': 10,
            'left': 'center'
        },
        'xAxis': {'type': 'value', 'name': x_column},
        'yAxis': {'type': 'value', 'name': y_column},
        'series': [
            {
                'data': scatter_data,
                'type': 'scatter',
                'name': 'Pontos de Dados',
                'itemStyle': {'opacity': 0.6},
                'symbolSize': 5  # Ajuste opcional para visualização
            },
            {
                'data': regression_line,
                'type': 'line',
                'name': 'Linha de Regressão',
                'lineStyle': {
                    'color': 'green',
                    'width': 2  # Reduz a espessura da linha pela metade
                },
                'showSymbol': False  # Remove os pontos na linha de regressão
            },
            {
                'data': confidence_area,
                'type': 'line',
                'name': 'Área de Confiança',
                'lineStyle': {'opacity': 0},
                'showSymbol': False,  # Remove os pontos na área de confiança
                'areaStyle': {'color': 'rgba(128, 128, 128, 0.25)'},
                'silent': True  # Evita interações com eventos de mouse
            },
        ],
        'grid': {'containLabel': True, 'left': '5%', 'right': '5%'},
    }

    # Aumenta a altura do gráfico para 600 pixels
    st_echarts(options=options, key=key, height=600)




# Função para gerar gráfico de linhas com regressão e área de confiança
def line_chart(dataframe, coluna, titulo="Gráfico de Linhas", key=None, nivel_confianca=95, valor_x=None):
    df = dataframe[coluna].dropna()
    x = df.index.map(pd.Timestamp.toordinal).values.reshape(-1, 1)
    y = df.values
    # Regressão linear
    model = LinearRegression()
    model.fit(x, y)
    y_pred = model.predict(x)

    # Intervalo de confiança
    n = len(x)
    t_value = stats.t.ppf((1 + nivel_confianca / 100) / 2, df=n - 2)
    residuals = y - y_pred
    std_error = np.sqrt(np.sum(residuals ** 2) / (n - 2))
    conf_interval = t_value * std_error * np.sqrt(1 / n + (x - np.mean(x)) ** 2 / np.sum((x - np.mean(x)) ** 2))
    conf_interval = conf_interval.flatten()  # Corrigir para serialização JSON

    # Ponto de previsão
    valor_y_previsto = None
    if valor_x is not None:
        valor_x_ordinal = pd.Timestamp(valor_x).toordinal()
        valor_y_previsto = model.predict([[valor_x_ordinal]])[0]

    # Dados para o gráfico
    data = [{'value': [str(index.date()), value]} for index, value in df.items()]
    regression_line = [{'value': [str(pd.Timestamp.fromordinal(int(x_val[0])).date()), y_val]} for x_val, y_val in zip(x, y_pred)]
    upper_conf = [{'value': [str(pd.Timestamp.fromordinal(int(x_val[0])).date()), y_val + ci]} for x_val, y_val, ci in zip(x, y_pred, conf_interval)]
    lower_conf = [{'value': [str(pd.Timestamp.fromordinal(int(x_val[0])).date()), y_val - ci]} for x_val, y_val, ci in zip(x, y_pred, conf_interval)]

    options = {
        'title': {'text': titulo},
        'tooltip': {'trigger': 'axis'},
        'xAxis': {
            'type': 'category',
            'data': [str(index.date()) for index in df.index],
            'name': 'Data',
            'nameLocation': 'middle',
            'nameGap': 25
        },
        'yAxis': {
            'type': 'value',
            'name': 'Valores',
            'nameLocation': 'middle',
            'nameRotate': 90,
            'nameGap': 50
        },
        'series': [
            {'data': data, 'type': 'line', 'name': 'Dados'},
            {'data': regression_line, 'type': 'line', 'name': 'Regressão', 'lineStyle': {'color': 'green'}},
            {'data': upper_conf, 'type': 'line', 'name': 'Limite Superior', 'lineStyle': {'type': 'dashed', 'color': 'yellow'}},
            {'data': lower_conf, 'type': 'line', 'name': 'Limite Inferior', 'lineStyle': {'type': 'dashed', 'color': 'yellow'}},
        ]
    }

    if valor_y_previsto is not None:
        options['series'].append({
            'data': [[str(valor_x), valor_y_previsto]],
            'type': 'scatter',
            'name': 'Previsão',
            'symbolSize': 10,
            'itemStyle': {'color': 'red'}
        })

    st_echarts(options=options, height="500px", key=key)




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

# Função de plotagem 3D modificada com variação de cores, opacidade e linha de regressão
def scatter_3d_plot(dataframe, x_column, y_column, z_column, normalize=False, title="3D Scatter Plot", key=None):
    from streamlit_echarts import st_echarts
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LinearRegression

    # Preparação dos dados
    df = dataframe[[x_column, y_column, z_column]].dropna()

    if normalize:
        df = (df - df.min()) / (df.max() - df.min())

    # Reset do índice para garantir que a sequência está correta
    df = df.reset_index(drop=True)

    # Criar uma coluna de sequência para visualMap (assumindo que os dados estão ordenados por data)
    df['sequence'] = df.index

    # Normalizar a sequência para [0, 1]
    df['sequence_normalized'] = (df['sequence'] - df['sequence'].min()) / (df['sequence'].max() - df['sequence'].min())

    # Dados dos pontos: [x, y, z, sequence_normalized]
    data_points = df[[x_column, y_column, z_column, 'sequence_normalized']].values.tolist()

    # Cálculo da regressão linear múltipla (Z = aX + bY + c)
    X = df[[x_column, y_column]].values
    y = df[z_column].values

    model = LinearRegression()
    model.fit(X, y)

    a = model.coef_[0]
    b = model.coef_[1]
    c = model.intercept_

    # Definir dois pontos para a linha de regressão com base nos valores mínimos e máximos de X e Y
    x_min, x_max = df[x_column].min(), df[x_column].max()
    y_min, y_max = df[y_column].min(), df[y_column].max()

    # Ponto 1: X = x_min, Y = y_min
    z1 = a * x_min + b * y_min + c
    point1 = [x_min, y_min, z1]

    # Ponto 2: X = x_max, Y = y_max
    z2 = a * x_max + b * y_max + c
    point2 = [x_max, y_max, z2]

    # Linha de regressão
    regression_line = [point1, point2]

    # Dados da linha de regressão: [x, y, z]
    regression_data = regression_line

    # Configuração das opções do ECharts
    options = {
        'title': {'text': title},
        'tooltip': {
            'formatter': """
                function (params) {
                    if (params.seriesType === 'scatter3D') {
                        return `(${params.value[0].toFixed(2)}, ${params.value[1].toFixed(2)}, ${params.value[2].toFixed(2)})`;
                    } else if (params.seriesType === 'line3D') {
                        return 'Linha de Regressão';
                    }
                    return '';
                }
            """
        },
        'visualMap': {
            'min': 0,
            'max': 1,
            'dimension': 3,  # A quarta dimensão (sequence_normalized)
            'inRange': {
                'color': ['#ff0000', '#0000ff']  # Gradiente do vermelho ao azul
            },
            'orient': 'vertical',
            'right': 10,
            'top': 'center',
            'show': True,
            'splitNumber': 5,
            'text': ['Mais Antigo', 'Mais Recente'],
            'textStyle': {
                'color': '#000'
            },
            'itemHeight': 200,
            'calculable': True
        },
        'xAxis3D': {'type': 'value', 'name': x_column},
        'yAxis3D': {'type': 'value', 'name': y_column},
        'zAxis3D': {'type': 'value', 'name': z_column},
        'grid3D': {
            'viewControl': {'projection': 'orthographic'},
            'boxWidth': 100,    # Conforme solicitado
            'boxHeight': 100,   # Conforme solicitado
            'boxDepth': 100     # Conforme solicitado
        },
        'series': [
            {
                'type': 'scatter3D',
                'name': 'Data',
                'data': data_points,
                'symbolSize': 5,
                'itemStyle': {
                    'opacity': 0.7  # Opacidade de 70%
                }
            },
            {
                'type': 'line3D',
                'name': 'Linha de Regressão',
                'data': regression_data,
                'lineStyle': {
                    'width': 2,
                    'color': '#00ff00'  # Cor verde para a linha de regressão
                },
                'symbolSize': 0,  # Remove símbolos nos pontos da linha
                'label': {
                    'show': False
                }
            },
        ],
    }

    # Renderiza o gráfico com altura aumentada
    st_echarts(options=options, key=key, height=800)