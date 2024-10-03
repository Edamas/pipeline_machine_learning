import streamlit as st
from preprocessing.null_handling import tratar_nulos
from preprocessing.normalization import normalizar

def value_manipulation_page(df_series):
    st.title("Manipulação de Valores")

    if df_series:
        serie_selecionada = st.selectbox("Selecione a Série para Manipulação de Valores", list(df_series.keys()))
        df = df_series[serie_selecionada]

        # Tratar valores nulos
        estrategia_nulos = st.radio("Escolha como tratar valores nulos", 
                                    ["Não Alterar", "Remover Nulos", "Preencher com Zero", "Preencher com Último Valor"], index=0)
        if estrategia_nulos != "Não Alterar" and st.button("Aplicar Tratamento de Nulos"):
            df = tratar_nulos(df, estrategia_nulos)
            st.success("Tratamento de nulos aplicado!")

        # Normalizar valores
        tipo_normalizacao = st.radio("Escolha a forma de normalização", 
                                     ["Não Alterar", "Entre 0 e 1", "Entre -1 e 1", "Desvio Padrão"], index=0)
        if tipo_normalizacao != "Não Alterar" and st.button("Aplicar Normalização"):
            df = normalizar(df, tipo_normalizacao)
            st.success("Normalização aplicada!")

        st.dataframe(df)
    else:
        st.error("Nenhum dado foi carregado para manipulação de valores.")
