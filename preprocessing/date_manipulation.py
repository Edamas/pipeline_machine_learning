import streamlit as st
from preprocessing.date_handling import preencher_datas_faltantes

def date_manipulation_page(df_series):
    st.title("Manipulação de Datas")

    if df_series:
        serie_selecionada = st.selectbox("Selecione a Série para Manipulação de Datas", list(df_series.keys()))
        df = df_series[serie_selecionada]

        # Regularizar datas
        frequencia = st.radio("Selecione a frequência", ["Não Alterar", "Diária", "Mensal", "Anual"], index=0)
        if frequencia != "Não Alterar" and st.button("Aplicar Regularização de Datas"):
            df = preencher_datas_faltantes(df, freq=frequencia)
            st.success("Regularização de datas aplicada com sucesso!")

        # Configurar período de interesse
        if 'data' in df.columns:
            data_inicio = st.date_input("Selecione a data de início", value=df['data'].min())
            data_fim = st.date_input("Selecione a data de fim", value=df['data'].max())
            df = df[(df['data'] >= pd.to_datetime(data_inicio)) & (df['data'] <= pd.to_datetime(data_fim))]
            st.success("Período configurado com sucesso!")

        st.dataframe(df)
    else:
        st.error("Nenhum dado foi carregado para manipulação de datas.")
