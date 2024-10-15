import streamlit as st
import pandas as pd
import numpy as np
from echarts_plots import grafico_scatterplot

# Função principal para correlações e scatterplots
def correlation_page():
    st.title("Correlação e Scatterplots")

    if "df_atualizado" in st.session_state and not st.session_state.df_atualizado.empty:
        df = st.session_state.df_atualizado.copy()

        # Selecione as colunas para visualizar a correlação
        st.subheader("Selecione as Séries para Análise de Correlação")
        colunas_disponiveis = df.columns.tolist()
        colunas_selecionadas = st.multiselect("Selecione as séries para gerar os scatterplots", colunas_disponiveis, default=colunas_disponiveis)

        # Scatterplot de correlação para todas as combinações de colunas
        if len(colunas_selecionadas) >= 2:
            for i in range(len(colunas_selecionadas)):
                for j in range(i + 1, len(colunas_selecionadas)):
                    serie_a = colunas_selecionadas[i]
                    serie_b = colunas_selecionadas[j]
                    df_corr = df[[serie_a, serie_b]].dropna()

                    if not df_corr.empty:
                        grafico_scatterplot(df_corr, coluna_x=serie_a, coluna_y=serie_b, titulo=f"Correlação entre {serie_a} e {serie_b}")
        else:
            st.warning("Selecione ao menos duas séries para gerar scatterplots.")
    else:
        st.error("Nenhum dado atualizado foi carregado para análise de correlação.")

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    correlation_page()