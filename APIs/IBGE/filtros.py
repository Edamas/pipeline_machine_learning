import streamlit as st
import pandas as pd
import numpy as np

# Função para aplicar filtros simplificados
def aplicar_filtros(df_metadados):
    col1, col2, col3 = st.columns([4, 1, 1])
    col2.metric(label="Tabelas Filtradas", value=len(st.session_state.get('sel_cod_tab', [])))
    col3.metric(label="Tabelas Totais", value=len(st.session_state['df_metadados_original']))
    
    if col1.checkbox('Usar filtros avançados'):
        with st.expander('Filtros', expanded=True):
            for column in df_metadados.columns:
                unique_values = df_metadados[column].dropna().unique()
                unique_values = sorted(unique_values, key=lambda x: str(x))
                
                # Slider duplo para colunas numéricas e datas
                if pd.api.types.is_numeric_dtype(df_metadados[column]) or pd.api.types.is_datetime64_any_dtype(df_metadados[column]):
                    min_val, max_val = df_metadados[column].min(), df_metadados[column].max()
                    selected_range = st.slider(f'Selecione o intervalo de {column}', min_val, max_val, (min_val, max_val))
                    df_metadados = df_metadados[(df_metadados[column] >= selected_range[0]) & (df_metadados[column] <= selected_range[1])]
                
                # DataFrame selecionável para itens únicos
                else:
                    df_unique_values = pd.DataFrame(unique_values, columns=[column])
                    from df_selecionavel import criar_dataframe_selecionavel  # Importar a função aqui
                    selected_values = criar_dataframe_selecionavel(df_unique_values, column, f'Selecione {column}', f'{column}_filter')
                    if selected_values:
                        df_metadados = df_metadados[df_metadados[column].isin(selected_values)]
    
    # Atualizar a seleção de tabelas filtradas
    st.session_state['sel_cod_tab'] = df_metadados.index.tolist()
    st.session_state['df_metadados'] = df_metadados