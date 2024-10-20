import streamlit as st
import pandas as pd

# Função para criar dataframes selecionáveis e armazenar a seleção
# Esta função exibe um DataFrame no Streamlit e permite ao usuário selecionar linhas específicas.
# A seleção é então retornada como uma lista de índices selecionados.
def criar_dataframe_selecionavel(df, titulo, descricao, df_key, hide_index=False):
    """
    Cria um DataFrame selecionável no Streamlit, permitindo ao usuário selecionar múltiplas linhas.

    Parâmetros:
    - df: DataFrame a ser exibido.
    - titulo: Título para exibir antes do DataFrame.
    - descricao: Descrição adicional para o DataFrame.
    - df_key: Chave para armazenar a seleção no session_state do Streamlit.
    - hide_index: Se True, oculta o índice do DataFrame.

    Retorna:
    - Uma lista dos índices das linhas selecionadas pelo usuário.
    """
    st.write(f"**{titulo}**: {descricao}")
    event = st.dataframe(df, use_container_width=True, hide_index=hide_index, on_select="rerun", selection_mode="single-row")

    # Armazena o número de registros filtrados
    st.session_state[f'{df_key}_filtrado'] = len(df)
    if event and 'selection' in event:
        if 'rows' in event['selection']:
            if event['selection']['rows']:
                return df.iloc[event['selection']['rows']].index.tolist()
    return []