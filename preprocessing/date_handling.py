# preprocessing/date_handling.py

import streamlit as st
import pandas as pd
# Remova ou comente a linha abaixo para evitar a importação circular
# from preprocessing.date_handling import preencher_datas_faltantes

def preencher_datas_faltantes(df, freq='D'):
    df = df.set_index('data')
    df = df.asfreq(freq)
    df = df.reset_index()
    return df

def date_handling_page():
    st.title("Manipulação de Datas")

    # Verificar se o DataFrame concatenado está disponível
    if "df_original" in st.session_state and not st.session_state.df_original.empty:
        df = st.session_state.df_original.copy()

        # Resetar o índice para ter a coluna 'data' disponível
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'data'}, inplace=True)

        # Seleção da série
        series_disponiveis = df.columns.tolist()
        series_disponiveis.remove('data')  # Remover a coluna 'data' da lista de séries
        serie_selecionada = st.selectbox("Selecione a Série para Manipulação de Datas", series_disponiveis)
        df_serie = df[['data', serie_selecionada]]

        # Regularizar datas
        st.subheader("Regularização de Datas")
        frequencia = st.radio("Selecione a frequência", ["Não Alterar", "Diária", "Mensal", "Anual"], index=0)
        if frequencia != "Não Alterar" and st.button("Aplicar Regularização de Datas"):
            freq_map = {"Diária": 'D', "Mensal": 'M', "Anual": 'Y'}
            df_serie = preencher_datas_faltantes(df_serie, freq=freq_map[frequencia])
            st.success("Regularização de datas aplicada com sucesso!")

        # Configurar período de interesse
        st.subheader("Configurar Período de Interesse")
        if 'data' in df_serie.columns:
            data_inicio = st.date_input("Selecione a data de início", value=df_serie['data'].min())
            data_fim = st.date_input("Selecione a data de fim", value=df_serie['data'].max())
            df_serie = df_serie[(df_serie['data'] >= pd.to_datetime(data_inicio)) & (df_serie['data'] <= pd.to_datetime(data_fim))]
            st.success("Período configurado com sucesso!")

        # Atualizar o DataFrame no session_state
        st.session_state.df_original = df_serie.set_index('data')

        # Exibir DataFrame atualizado
        st.subheader("Dados Atualizados")
        st.dataframe(df_serie)

    else:
        st.error("Nenhum dado foi carregado para manipulação de datas.")
