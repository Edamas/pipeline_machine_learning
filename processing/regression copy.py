import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from streamlit_echarts import st_echarts
import scipy.stats as stats
from manager import series_manager  # Adicionando a importação

# Função auxiliar para criar layout de colunas com títulos e widgets
def criar_layout_colunas(titulo, numerical_columns_list):
    cols = st.columns([1] + [1] * len(numerical_columns_list))
    cols[0].markdown(f"**{titulo}**")
    return cols

# Função para configurar a análise
def configurar_analise():
    regression_type = st.radio(
        "Tipo de Regressão",
        ('Linear', 'Polinomial', 'Exponencial/Potência', 'Logarítmica'),
        index=0,
        horizontal=True,
        key="regression_type_main"
    )
    return regression_type

def scatter_3d_plot(dataframe, x_column, y_column, z_column, title="3D Scatter Plot", key=None, regression_type='Linear'):
    df = dataframe[[x_column, y_column, z_column]].dropna()  # Remove NaN

    # Verifica se há dados suficientes
    if df.empty:
        st.error("Dados insuficientes para plotar o gráfico 3D.")
        return

    data_points = df[[x_column, y_column, z_column]].values.tolist()

    # Cálculo da regressão
    X = df[[x_column, y_column]].values
    y = df[z_column].values

    if regression_type == 'Linear':
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
    elif regression_type == 'Polinomial':
        from sklearn.preprocessing import PolynomialFeatures
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        model = LinearRegression()
        model.fit(X_poly, y)
        y_pred = model.predict(X_poly)
    elif regression_type == 'Exponencial':
        y_log = np.log1p(y)
        model = LinearRegression()
        model.fit(X, y_log)
        y_pred = np.expm1(model.predict(X))
    elif regression_type == 'Logarítmica':
        X_log = np.log1p(X)
        model = LinearRegression()
        model.fit(X_log, y)
        y_pred = model.predict(X_log)

    # Definindo os limites para a superfície de regressão
    x_min, x_max = df[x_column].min(), df[x_column].max()
    y_min, y_max = df[y_column].min(), df[y_column].max()
    x_range = np.linspace(x_min, x_max, 10)
    y_range = np.linspace(y_min, y_max, 10)
    xx, yy_grid = np.meshgrid(x_range, y_range)

    if regression_type == 'Linear':
        zz = model.coef_[0] * xx + model.coef_[1] * yy_grid + model.intercept_
    elif regression_type == 'Polinomial':
        zz = (model.coef_[0] + model.coef_[1] * xx + model.coef_[2] * yy_grid +
              model.coef_[3] * (xx ** 2) + model.coef_[4] * (yy_grid ** 2) +
              model.coef_[5] * (xx * yy_grid))
    elif regression_type == 'Exponencial':
        zz_log = model.coef_[0] * xx + model.coef_[1] * yy_grid + model.intercept_
        zz = np.expm1(zz_log)
    elif regression_type == 'Logarítmica':
        zz = model.coef_[0] * np.log1p(xx) + model.coef_[1] * np.log1p(yy_grid) + model.intercept_

    zz_flat = zz.flatten()
    xx_flat = xx.flatten()
    yy_flat = yy_grid.flatten()
    regression_surface = [list(point) for point in zip(xx_flat.tolist(), yy_flat.tolist(), zz_flat.tolist())]

    # Configuração das opções do ECharts
    options = {
        'title': {'text': title},
        'tooltip': {
            'formatter': """
                function (params) {
                    if (params.seriesType === 'scatter3D') {
                        return `(${params.value[0].toFixed(2)}, ${params.value[1].toFixed(2)}, ${params.value[2].toFixed(2)})`;
                    } else if (params.seriesType === 'surface') {
                        return 'Superfície de Regressão';
                    }
                    return '';
                }
            """
        },
        'visualMap': {
            'min': 0,
            'max': 1,
            'dimension': 3,
            'inRange': {
                'color': ['#ff0000', '#0000ff']  # Gradiente do vermelho ao azul
            },
            'orient': 'vertical',
            'right': 10,
            'top': 'center',
            'show': True,
        },
        'xAxis3D': {'type': 'value', 'name': x_column},
        'yAxis3D': {'type': 'value', 'name': y_column},
        'zAxis3D': {'type': 'value', 'name': z_column},
        'grid3D': {
            'viewControl': {'projection': 'orthographic'},
            'boxWidth': 100,
            'boxHeight': 100,
            'boxDepth': 100
        },
        'series': [
            {
                'type': 'scatter3D',
                'name': 'Dados',
                'data': data_points,
                'symbolSize': 5,
                'itemStyle': {
                    'opacity': 0.7
                }
            },
            {
                'type': 'surface',
                'name': 'Superfície de Regressão',
                'data': regression_surface,
                'opacity': 0.5,
                'itemStyle': {
                    'color': '#00ff00',
                    'opacity': 0.5,
                }
            },
        ],
    }

    st_echarts(options=options, key=key, height=800)

def visualizar_grafico(selected_series, regression_type, df, confidence_level=0.95):
    if not selected_series:
        return

    num_selected = len(selected_series)

    df = df.dropna(subset=selected_series)

    if num_selected == 1:
        selected_col = selected_series[0]
        options = {
            'title': {'text': f"Gráfico de Linha: {selected_col}"},
            'tooltip': {'trigger': 'axis'},
            'xAxis': {'type': 'category', 'data': df.index.strftime('%Y-%m-%d').tolist()},
            'yAxis': {'type': 'value', 'name': selected_col},
            'series': [{
                'data': df[selected_col].dropna().tolist(),  # Remove NaN aqui
                'type': 'line',
                'smooth': True,
                'itemStyle': {
                    'opacity': 0.7,
                    'color': '#ff0000'
                }
            }]
        }
        st_echarts(options=options, key=f"line_chart_{selected_col}", height=300)

    elif num_selected == 2:
        x_col, y_col = selected_series[:2]

        # Preparação dos dados para regressão
        X = df[x_col].dropna().values.reshape(-1, 1)  # Remove NaN
        Y = df[y_col].dropna().values

        # Verifica se os dados não estão vazios
        if len(X) == 0 or len(Y) == 0:
            st.error("Dados insuficientes para calcular a regressão.")
            return

        model = LinearRegression()
        model.fit(X, Y)
        Y_pred = model.predict(X)
        y_pred = np.nan_to_num(y_pred)
        conf_interval = np.nan_to_num(conf_interval)
        if np.isnan(y_pred).any() or np.isinf(y_pred).any():
            st.error("Erro ao calcular os valores previstos. Verifique os dados de entrada.")
            return

        if np.isnan(conf_interval).any() or np.isinf(conf_interval).any():
            st.error("Erro ao calcular o intervalo de confiança. Verifique os dados de entrada.")
            return


        # Intervalo de confiança
        n = len(X)
        t_value = stats.t.ppf((1 + confidence_level) / 2, n - 2)
        residuals = Y - Y_pred
        std_error = np.std(residuals)
        conf_interval = t_value * std_error * np.sqrt(1 / n + (X.flatten() - np.mean(X.flatten())) ** 2 / np.sum((X.flatten() - np.mean(X.flatten())) ** 2))

        # Dados para o gráfico
        data = [[x, y] for x, y in zip(df[x_col], df[y_col])]
        upper_bound = Y_pred + conf_interval
        lower_bound = Y_pred - conf_interval

        # Configuração do gráfico
        options = {
            'title': {'text': f"Scatter Plot: {x_col} vs {y_col}"},
            'tooltip': {'trigger': 'axis'},
            'xAxis': {'type': 'value', 'name': x_col},
            'yAxis': {'type': 'value', 'name': y_col},
            'series': [
                {
                    'type': 'scatter',
                    'data': data,
                    'symbolSize': 5,
                    'itemStyle': {
                        'opacity': 0.7,
                        'color': '#ff0000'
                    }
                },
                {
                    'type': 'line',
                    'data': [[x, y] for x, y in zip(df[x_col], Y_pred)],
                    'lineStyle': {
                        'width': 2,
                        'color': '#0000ff'  # Cor da linha de regressão
                    }
                },
                {
                    'type': 'line',
                    'data': [[x, ub] for x, ub in zip(df[x_col], upper_bound)],
                    'lineStyle': {
                        'type': 'dashed',
                        'color': 'rgba(128, 128, 128, 0.5)'  # Limite superior
                    },
                },
                {
                    'type': 'line',
                    'data': [[x, lb] for x, lb in zip(df[x_col], lower_bound)],
                    'lineStyle': {
                        'type': 'dashed',
                        'color': 'rgba(128, 128, 128, 0.5)'  # Limite inferior
                    },
                }
            ]
        }

        st_echarts(options=options, key=f"scatter_plot_{x_col}_{y_col}", height=500)

def exibir_resumo(selected_series, y_pred, r2):
    with st.expander("Resumo Estatístico"):
        cols = criar_layout_colunas("Resumo Estatístico", st.session_state['numerical_columns'])

        summary_df = pd.DataFrame()
        for col in selected_series:
            summary_df[col] = st.session_state['df_main'][col].dropna()  # Remove NaN aqui

        st.table(summary_df)

        if y_pred is not None:
            for col in selected_series:
                if col == selected_series[-1]:  # Se for a última coluna (Y)
                    st.markdown(f"**Previsão de {col}: {y_pred:.4f}**")

def ajustar_valores(selected_series, df):
    if not selected_series:
        return None

    inputs = []
    cols = criar_layout_colunas("Ajuste de Valores", selected_series)
    
    for i, col in enumerate(selected_series):
        with cols[i + 1]:
            min_val = float(df[col].min())
            max_val = float(df[col].max())
            slider_val = st.slider(
                f"Selecionar {col}",
                min_value=min_val,
                max_value=max_val,
                value=min_val,
                step=(max_val - min_val) / 100 if (max_val - min_val) != 0 else 1,
                key=f"slider_{col}"
            )
            inputs.append(slider_val)

    # Calcular y_pred
    y_pred = None
    if len(selected_series) == 1:
        X = df[selected_series].dropna().values.reshape(-1, 1)
        y = df[selected_series[-1]].dropna().values
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict([[inputs[0]]])[0]
    elif len(selected_series) == 2:
        X = df[selected_series[:2]].dropna().values
        y = df[selected_series[-1]].dropna().values
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict([inputs[:2]])[0]
    elif len(selected_series) == 3:
        X = df[selected_series[:3]].dropna().values
        y = df[selected_series[-1]].dropna().values
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict([inputs])[0]

    return y_pred

def inicializar():
    
    if "df_main" in st.session_state:
        if not st.session_state['df_main'].empty:
            if pd.api.types.is_datetime64_any_dtype(st.session_state['df_main'].index):
                st.session_state['numerical_columns'] = st.session_state['df_main'].select_dtypes(include=[np.number]).columns.tolist()
                return True
            else:
                st.error("O índice do DataFrame não é do tipo datetime.")
    st.warning("Por favor, carregue uma ou mais séries válidas antes de prosseguir.")
    return False


def regression_page():
    st.title("Análise Estatística e de Correlação")

    # Chamada da função para gerenciar as séries
    series_manager()

    if inicializar():
        selected_series = {'X': [], 'y': None}

        # Exibir Nome da Série
        cols = criar_layout_colunas("Nome da Série", ["Data"] + st.session_state['numerical_columns'])
        for i, col in enumerate(["Data"] + st.session_state['numerical_columns']):
            with cols[i + 1]:
                st.markdown(f"**{col}**")

        # Adicionar datas ao DataFrame
        data_dates = st.session_state['df_main'].index.strftime('%Y-%m-%d').tolist()

        # Estrutura de seleção de séries como X (inputs)
        cols = criar_layout_colunas(":blue[**X** (*input*)]", st.session_state['numerical_columns'])
        for i, col in enumerate(st.session_state['numerical_columns']):
            with cols[i + 1]:
                if col == "Data":
                    usar_x = st.checkbox("Data", key=f"usar_x_{col}_{i}", value=True)  # Data como X pré-selecionado
                    selected_series['X'].append(col)  # Adiciona Data como X automaticamente
                else:
                    usar_x = st.checkbox(col[:3], key=f"usar_x_{col}_{i}", value=False)
                    if usar_x:
                        selected_series['X'].append(col)

                # Desabilitar checkbox de Y correspondente
                if col in selected_series['X']:
                    st.session_state[f"usar_y_{col}"] = False  # Desabilita checkbox de Y

        # Estrutura de seleção de séries como Y (target)
        cols = criar_layout_colunas(":red[**Y** (*target*)]", st.session_state['numerical_columns'])
        for i, col in enumerate(st.session_state['numerical_columns']):
            with cols[i + 1]:
                if col == "Data":
                    st.checkbox("Data", key=f"usar_y_{col}_{i}", value=False, disabled=True)  # Data não pode ser Y
                else:
                    usar_y = st.checkbox(col[:3], key=f"usar_y_{col}_{i}", value=False)
                    # Desabilitar se já tiver X selecionado
                    if col in selected_series['X']:
                        usar_y = st.checkbox(col[:3], key=f"usar_y_{col}_{i}", value=False, disabled=True)
                    if usar_y:
                        selected_series['y'] = col

        # Verificação se uma série Y foi selecionada
        if selected_series['y'] is None:
            st.info("Ao menos uma série deve ser selecionada como Y (target) para iniciar a análise.")
            return

        # Limitar a seleção de séries
        if len(selected_series['X']) > 3:  # Permite no máximo 3 séries X
            st.warning("Não é possível exibir mais do que três séries X ao mesmo tempo.")
            return

        # Exibir valores para Y
        y_col = selected_series['y']
        y_value = st.number_input(f"Valor para {y_col}", value=0.0)  # Input para Y

        # Exibir valores para X
        y_pred_values = []
        for x_col in selected_series['X']:
            value = st.number_input(f"Valor para {x_col}", value=0.0)  # Input para cada X
            y_pred_values.append(value)

        # Exibir valores selecionados
        if y_pred_values:  # Verifica se há valores para X
            st.markdown(f"**Valores selecionados para X:** {y_pred_values}  | **Valor para Y:** {y_value:.4f}", unsafe_allow_html=True)

        # Visualizar gráficos (se necessário)
        if len(selected_series['X']) <= 3:
            visualizar_grafico(selected_series, "Tipo de Regressão", st.session_state['df_main'])
        else:
            st.warning("A análise não pode ser apresentada em gráfico devido ao número excessivo de séries selecionadas.")

        # Exibir resumo estatístico (OLS)
        exibir_resumo(selected_series, st.session_state['df_main'], y_pred_values)
# Chamada da função principal fora de qualquer outra função
if __name__ == '__main__':
    regression_page()
