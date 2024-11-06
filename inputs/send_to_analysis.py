import streamlit as st
import pandas as pd

def send_to_analysis(new_series):
    """
    Função para concatenar a série recebida com o dataframe da sessão, ou criar um novo.
    """
    # Obter ou inicializar o DataFrame na sessão
    df = st.session_state.get('df_main', pd.DataFrame())

    # Identificar e converter o formato de índice de data em new_series
    if not pd.api.types.is_datetime64_any_dtype(new_series.index):
        try:
            new_series.index = pd.to_datetime(new_series.index, dayfirst=True, errors='coerce')
        except Exception as e:
            st.error(f"Erro ao converter índice de data: {e}")
            return False

    # Sobrescrever colunas duplicadas, se existirem
    for col in new_series.columns.intersection(df.columns):
        st.warning(f'A coluna "{col}" já existe no dataframe. Sobrescrevendo...')
        df.drop(columns=[col], inplace=True)

    # Concatenar a nova série ao DataFrame existente
    df = pd.concat([df, new_series], axis=1)
    df.index = pd.to_datetime(df.index, errors='coerce', dayfirst=True)
    df.index.name = 'data'
    df = df.sort_index().groupby(df.index).sum(min_count=1)

    # Atualizar o DataFrame na sessão
    st.session_state['df_main'] = df

    enviado = True
    for column in new_series.columns:
        if column not in st.session_state['df_main'].columns:
            enviado = False
    return enviado
    # incluir mensagem
    # mesclar com df_original
