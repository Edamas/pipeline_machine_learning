import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import statsmodels.api as sm
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import r2_score
from manager import series_manager

# Função auxiliar para converter datas para floats
def converter_datas_para_float(df):
    df_float = df.copy()
    df_float['Data'] = df_float.index.year + (df_float.index.dayofyear - 1) / 365.25
    return df_float

# Função auxiliar para criar layout de colunas com títulos e widgets
def criar_layout_colunas(titulo, numerical_columns_list):
    cols = st.columns([1] + [1] * len(numerical_columns_list))
    cols[0].markdown(f"**{titulo}**")
    return cols

# Função para inicializar e verificar se os dados estão carregados corretamente
def inicializar():
    if "df_temp_editado" in st.session_state:
        if not st.session_state['df_temp_editado'].empty:
            if pd.api.types.is_datetime64_any_dtype(st.session_state['df_temp_editado'].index):
                st.session_state['numerical_columns'] = st.session_state['df_temp_editado'].select_dtypes(include=[np.number]).columns.tolist()
                return True
            else:
                st.error("O índice do DataFrame não é do tipo datetime.")
    st.warning("Por favor, carregue uma ou mais séries válidas antes de prosseguir.")
    return False

# Função para exibir a previsão e o relatório OLS
def exibir_relatorio_regressao(X, Y, regression_type, confidence_level):
    if regression_type == 'Linear':
        X_const = sm.add_constant(X)
        model = sm.OLS(Y, X_const).fit()
    elif regression_type == 'Polinomial':
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        X_const = sm.add_constant(X_poly)
        model = sm.OLS(Y, X_const).fit()
    elif regression_type == 'Logística':
        model = LogisticRegression()
        model.fit(X, Y)
    elif regression_type == 'Logarítmica':
        X_log = np.log(X + 1)
        X_const = sm.add_constant(X_log)
        model = sm.OLS(Y, X_const).fit()
    else:
        st.error("Tipo de regressão não implementado ainda.")
        return None

    st.subheader("Relatório de Regressão")
    st.text(model.summary())

    return model

# Função para exibir gráfico 2D usando Plotly
def plot_2d(df, x_column, y_column, y_pred, upper_bound, lower_bound, y_pred_point, confidence_level):
    fig = go.Figure()

    # Scatterplot dos dados originais
    fig.add_trace(go.Scatter(x=df[x_column], y=df[y_column], mode='markers', name=y_column, marker=dict(size=2)))  # Tamanho reduzido dos pontos

    # Linha de Regressão
    fig.add_trace(go.Scatter(x=df[x_column], y=y_pred, mode='lines', name="Linha de Regressão", line=dict(color='red')))

    # Área de confiança
    fig.add_trace(go.Scatter(x=np.concatenate([df[x_column], df[x_column][::-1]]),
                             y=np.concatenate([upper_bound, lower_bound[::-1]]),
                             fill='toself',
                             fillcolor='rgba(128, 128, 128, 0.5)',
                             line=dict(color='rgba(255,255,255,0)'),
                             hoverinfo="skip",
                             showlegend=False))

    # Ponto previsto
    fig.add_trace(go.Scatter(x=[df[x_column].iloc[-1]], y=[y_pred_point], mode='markers', name="Y Previsto", marker=dict(color='green', size=10)))

    st.plotly_chart(fig)

# Função principal para a página de regressão
def regression_page():
    st.title("Análise Estatística e de Regressão")

    # Chamada da função para gerenciar as séries
    series_manager()

    if inicializar():
        selected_series = {'X': [], 'y': None}

        # Exibir Nome da Série
        cols = criar_layout_colunas("Nome da Série", ["Data"] + st.session_state['numerical_columns'])
        for i, col in enumerate(["Data"] + st.session_state['numerical_columns']):
            with cols[i + 1]:
                st.markdown(f"**{col}**")

        # Estrutura de seleção de séries como X (inputs)
        cols = criar_layout_colunas(":blue[**X** (*input*)]", st.session_state['numerical_columns'])
        for i, col in enumerate(st.session_state['numerical_columns']):
            with cols[i + 1]:
                usar_x = st.checkbox(col[:3], key=f"usar_x_{col}_{i}", value=False)
                if usar_x:
                    selected_series['X'].append(col)

        # Estrutura de seleção de séries como Y (target)
        cols = criar_layout_colunas(":red[**Y** (*target*)]", st.session_state['numerical_columns'])
        for i, col in enumerate(st.session_state['numerical_columns']):
            with cols[i + 1]:
                usar_y = st.checkbox(col[:3], key=f"usar_y_{col}_{i}", value=False)
                if usar_y:
                    selected_series['y'] = col

        # Verificação se uma série Y foi selecionada
        if selected_series['y'] is None:
            st.info("Ao menos uma série deve ser selecionada como Y (target) para iniciar a análise.")
            return

        # Verificação do número de colunas X selecionadas
        if len(selected_series['X']) > 3:
            st.warning("Não é possível exibir mais do que três séries X ao mesmo tempo.")
            return

        # Slider para o nível de confiança
        confidence_level = st.slider("Nível de Confiança (%)", min_value=80, max_value=99, value=95, step=1) / 100

        # Preparação dos dados usando df_temp_editado
        df = st.session_state['df_temp_editado']
        df = converter_datas_para_float(df)  # Converter datas para floats

        # Previsão de Y
        X = df[selected_series['X']].dropna()
        Y = df[selected_series['y']].dropna()

        # Verificação se há dados suficientes
        if X.empty or Y.empty:
            st.error("Dados insuficientes para calcular a regressão.")
            return

        # Selecionar o tipo de regressão
        regression_type = st.radio("Tipo de Regressão", ['Linear', 'Polinomial', 'Logística', 'Logarítmica'])

        # Exibir relatório de regressão e obter modelo
        model = exibir_relatorio_regressao(X, Y, regression_type, confidence_level)

        # Fazer previsões
        X_const = sm.add_constant(X)
        y_pred = model.predict(X_const)

        # Calcular intervalo de confiança
        pred_var = model.get_prediction(X_const).conf_int(alpha=1 - confidence_level)
        lower_bound = pred_var[:, 0]
        upper_bound = pred_var[:, 1]

        # Calcular previsão de Y para o último ponto de X
        last_X = X.iloc[-1].values.reshape(1, -1)  # Garantir o alinhamento correto das dimensões
        last_X_const = np.insert(last_X, 0, 1)  # Adicionar manualmente o valor 1 para a constante
        y_pred_point = model.predict(last_X_const.reshape(1, -1))[0]

        # Exibir previsão de Y
        st.markdown(f"**Previsão para Y (último ponto):** {y_pred_point:.4f}")

        # Visualização dos gráficos
        if len(selected_series['X']) == 1:  # Gráfico 2D com Data como eixo X
            plot_2d(df, selected_series['X'][0], selected_series['y'], y_pred, upper_bound, lower_bound, y_pred_point, confidence_level)
        elif len(selected_series['X']) == 2:  # Gráfico 3D com duas séries X e uma Y
            plot_3d(df, selected_series['X'], selected_series['y'], y_pred, y_pred_point)
        else:
            st.warning("Não é possível exibir gráficos com mais de três séries X selecionadas. Estatísticas OLS e fórmula continuam disponíveis.")
        
        # Coluna para os sliders e markdown de valores de predição
        for i, x_col in enumerate(selected_series['X']):
            st.markdown(f"**Valor de {x_col}**")
            slider_value = st.slider(f"Selecione o valor de {x_col}", float(X[x_col].min()), float(X[x_col].max()), float(X[x_col].mean()))
            st.markdown(f"**Valor predito de Y:** {y_pred_point:.4f}")

# Função principal
if __name__ == '__main__':
    regression_page()
