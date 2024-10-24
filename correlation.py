import streamlit as st
import pandas as pd
import numpy as np
from echarts_plots import grafico_scatterplot
from sklearn.linear_model import LinearRegression

# Função principal para correlações e scatterplots
def correlation_page():
    st.title("Correlação, Scatterplots, Linha de Regressão e Previsão")

    if "df_original" in st.session_state and not st.session_state.df_original.empty:
        df = st.session_state.df_original.copy()

        # Selecione as colunas para visualizar a correlação
        st.header("Selecione as Séries para Análise de Correlação")
        colunas_disponiveis = df.columns.tolist()
        col_input, col_output = st.columns(2)
        col_input.subheader('Eixo :red[x]')
        coluna_x = col_input.radio("", colunas_disponiveis, key="coluna_x", horizontal=False)
        colunas_disponiveis_y = [col for col in colunas_disponiveis if col != coluna_x]
        col_output.subheader('Eixo :blue[y]')
        coluna_y = col_output.radio("", colunas_disponiveis_y, key="coluna_y", horizontal=False)

        # Scatterplot de correlação para o par de colunas selecionado
        if coluna_x and coluna_y:
            df_corr = df[[coluna_x, coluna_y]].dropna()
            if not df_corr.empty:
                # Ajuste da regressão linear
                x = df_corr[coluna_x].values.reshape(-1, 1).tolist()
                y = df_corr[coluna_y].values.reshape(-1, 1).tolist()
                reg = LinearRegression().fit(x, y)
                y_pred = reg.predict(x).flatten().tolist()
                r2 = reg.score(x, y)

                # Definir os limites dos eixos com base nos valores dos pontos
                x_min, x_max = min(x)[0], max(x)[0]
                y_min, y_max = min(y)[0], max(y)[0]
                x_min_plot = x_min - 0.1 * (x_max - x_min)
                x_max_plot = x_max + 0.1 * (x_max - x_min)
                y_min_plot = y_min - 0.1 * (y_max - y_min)
                y_max_plot = y_max + 0.1 * (y_max - y_min)

                ponto_selecionado = []
                if coluna_x and coluna_y:
                    col_input, col_output = st.columns(2)
                    col_input.subheader(f':red[{coluna_x}] (*input*)')
                    col_output.subheader(f':blue[{coluna_y}] (*output*)')
                    
                    entrada = col_input.container(border=True, height=150)
                    entrada.markdown(f"Informe o valor de entrada para o eixo :red[x] (*input*) :red[{coluna_x}]:")
                    valor_x = entrada.slider('', float(x_min_plot), float(x_max_plot), step=(x_max - x_min) / 10000, value = np.average(x), key=f"slider_{coluna_x}_{coluna_y}")
                    delta = r2 ** 0.5
                    if delta >= 0.5:
                        delta_color = 'normal'
                    elif -0.5 < delta < 0.5:
                        delta_color = 'off'
                    else:
                        delta_color = 'normal'
                    determ = col_output.container(border=True, height=150)
                    determ.metric(label=f'Índice de Determinância (**R²**) e Coeficiente de Correlação (**R**)', value=r2, delta=delta, delta_color=delta_color)
                    if reg.intercept_[0] >= 0:
                        determ.markdown(f"##### Fórmula: y = `{reg.coef_[0][0]:,}x` + `{reg.intercept_[0]:,}`")
                    else:
                        determ.markdown(f'##### Fórmula: :blue[y] = `{reg.coef_[0][0]:,}`:red[x]  `{reg.intercept_[0]:,}`')
                    valor_y_previsto = reg.predict([[valor_x]])[0]
                    x_selec = col_input.container(border=True, height=100)
                    x_selec.metric(label=f"Valor Selecionado para `{coluna_x}`", value=f"{valor_x:,}")
                    y_pred = col_output.container(border=True, height=100)
                    y_pred.metric(label=f"Valor Previsto de `{coluna_y}`", value=f"{valor_y_previsto[0]:,}")
                    
                    with st.expander('Estatísticas:', expanded=False):
                        st.markdown(
                            f"- Coeficiente de Correlação (R): `{r2 ** 0.5:.4f}`\n"
                            f"- Índice de Determinância (R²): `{r2:.4f}` *(o quanto, de 0 a 1, uma série 'explica' a outra)*\n"
                            f"- Média de {coluna_x}: `{df_corr[coluna_x].mean():,}`\n"
                            f"- Média de {coluna_y}: `{df_corr[coluna_y].mean():,}`\n"
                            f"- Variância de {coluna_x}: `{df_corr[coluna_x].var():,}`\n"
                            f"- Variância de {coluna_y}: `{df_corr[coluna_y].var():,}`\n"
                            f"- Fórmula da Regressão: y = `{reg.coef_[0][0]:.4f}x + {reg.intercept_[0]:.4f}`"
                        )
                    ponto_selecionado = [[valor_x, valor_y_previsto[0]]]
                    # Scatterplot
                    grafico_scatterplot(
                        dataframe=df_corr,
                        coluna_x=coluna_x,
                        coluna_y=coluna_y,
                        titulo=f"Correlação entre {coluna_x} e {coluna_y}",
                        key=f"scatter_{coluna_x}_{coluna_y}",
                        x_min_plot=x_min_plot,
                        x_max_plot=x_max_plot,
                        y_min_plot=y_min_plot,
                        y_max_plot=y_max_plot,
                        reg=reg,
                        ponto_selecionado=ponto_selecionado,
                        valor_x=valor_x,
                        valor_y_previsto=valor_y_previsto,
                    )

                    # Tabela
                    with st.expander('Dados', expanded=False):
                        st.dataframe(df_corr[[coluna_x, coluna_y]], hide_index=True, use_container_width=True, key=f"dataframe_xy_{coluna_x}_{coluna_y}")
                else:
                    st.error('É necessário definir as variáveis x e y')

                

                

            else:
                st.warning("Os dados selecionados não contêm valores suficientes para gerar o scatterplot.")
        else:
            st.warning("Selecione ao menos duas séries para gerar o scatterplot.")
    else:
        st.error("Nenhum dado atualizado foi carregado para análise de correlação.")

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    correlation_page()
