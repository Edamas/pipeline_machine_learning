import streamlit as st
import pandas as pd

# Função de normalização
def normalizar(df, tipo_normalizacao):
    # Selecionar as colunas numéricas para normalização
    numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns
    if len(numeric_columns) > 0:
        if tipo_normalizacao == "Entre 0 e 1":
            df[numeric_columns] = (df[numeric_columns] - df[numeric_columns].min()) / (df[numeric_columns].max() - df[numeric_columns].min())
        elif tipo_normalizacao == "Entre -1 e 1":
            df[numeric_columns] = 2 * (df[numeric_columns] - df[numeric_columns].min()) / (df[numeric_columns].max() - df[numeric_columns].min()) - 1
        elif tipo_normalizacao == "Desvio Padrão em torno de 0":
            df[numeric_columns] = (df[numeric_columns] - df[numeric_columns].mean()) / df[numeric_columns].std()
        else:
            st.warning("Seleção de normalização inválida.")
        
        # Atualizar o dataframe no estado
        st.session_state.df_series['serie_selecionada'] = df
        
        # Mostrar sucesso e o DataFrame normalizado
        st.success("Normalização aplicada com sucesso!")
        return df  # Retorna o DataFrame atualizado
    else:
        st.warning("Nenhuma coluna numérica encontrada para normalização.")
        return df  # Retorna o DataFrame original se nenhuma coluna numérica for encontrada
