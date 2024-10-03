import streamlit as st
import pandas as pd

# Exemplo de função para tratar valores
def tratar_nulos(df, estrategia):
    if estrategia == "Remover Nulos":
        return df.dropna()
    elif estrategia == "Preencher com Zero":
        return df.fillna(0)
    elif estrategia == "Preencher com Último Valor":
        return df.fillna(method="ffill")
    elif estrategia == "Preencher com Próximo Valor":
        return df.fillna(method="bfill")
    elif estrategia == "Preencher com Média":
        return df.fillna(df.mean())
    return df

def value_handling_page(df_series):
    st.title("Manipulação de Valores")

    if df_series:
        serie_selecionada = st.selectbox("Selecione a Série para Manipulação de Valores", list(df_series.keys()))
        df = df_series[serie_selecionada]

        estrategia_nulos = st.radio("Escolha como tratar valores nulos", 
                                    ["Não Alterar", "Remover Nulos", "Preencher com Zero", 
                                     "Preencher com Último Valor", "Preencher com Próximo Valor", "Preencher com Média"], index=0)

        if st.button("Aplicar Tratamento de Nulos"):
            df = tratar_nulos(df, estrategia_nulos)
            st.success("Tratamento de nulos aplicado com sucesso!")
            st.dataframe(df)

        # Atualiza os dados no session_state
        st.session_state.df_series[serie_selecionada] = df
    else:
        st.error("Nenhum dado foi carregado para manipulação de valores.")
