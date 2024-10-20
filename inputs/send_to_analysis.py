import streamlit as st
import pandas as pd

def handle_duplicate_columns(ts):
    """
    Função para tratar colunas duplicadas, permitindo que o usuário escolha 
    entre sobrescrever ou cancelar.
    """
    col_dup_responses = []

    # Encontrar colunas duplicadas
    duplicated_columns = ts.columns[ts.columns.duplicated()].unique()
    
    # Caso existam colunas duplicadas, perguntar ao usuário o que fazer
    for col in duplicated_columns:
        resposta = st.radio(
            f'A coluna "{col}" já existe. O que deseja fazer?',
            ['Sobrescrever', 'Cancelar'],
            index=None,
            key=f'duplicated_{col}'
        )
        col_dup_responses.append((col, resposta))

    # Processar respostas de colunas duplicadas
    for col, resposta in col_dup_responses:
        if resposta == 'Sobrescrever':
            # Sobrescrever significa remover a coluna 
            ts.drop(columns=[col], inplace=True)
        elif resposta == 'Cancelar':
            # Cancelar a operação para evitar problemas
            st.warning("Operação cancelada pelo usuário. Nenhum dado foi enviado para análise.")
            return False

    return True


def send_to_analysis(dataframe):
    """
    Função para enviar os dados para análise.
    Realiza o tratamento de colunas duplicadas e verifica se os dados estão prontos para envio.
    """
    # Verificar se existe um dataframe de análise na sessão
    if 'df_original' not in st.session_state:
        st.session_state['df_original'] = pd.DataFrame()

    existing_analysis_df = st.session_state['df_original']

    # Verificar se as colunas do dataframe já existem no dataframe de análise
    existing_columns = existing_analysis_df.columns.intersection(dataframe.columns)
    
    continuar = False
    if not existing_columns.empty:
        col_dup_responses = []
        for col in existing_columns:
            resposta = st.radio(
                f'A coluna "{col}" já existe no dataframe de análise. O que deseja fazer?',
                ['Sobrescrever', 'Cancelar'],
                index=None,
                key=f'analysis_duplicated_{col}'
            )
            col_dup_responses.append((col, resposta))

        # Processar respostas de colunas duplicadas
        for col, resposta in col_dup_responses:
            if resposta == 'Sobrescrever':
                existing_analysis_df.drop(columns=[col], inplace=True)
                continuar = True
            elif resposta == 'Cancelar':
                st.warning("Operação cancelada pelo usuário. Nenhum dado foi enviado para análise.")
                return False
    else:
        continuar = True
    
    if continuar:
        # Tratar colunas duplicadas no próprio dataframe
        if not handle_duplicate_columns(dataframe):
            return False

        # Concatenar a nova série com as séries existentes, combinando índices e mantendo valores únicos
        combined_df = pd.concat([existing_analysis_df, dataframe], axis=1)
        combined_df.index = pd.to_datetime(combined_df.index, errors='coerce', dayfirst=True)
        combined_df = combined_df.sort_index()

        # Para índices duplicados, manter valores únicos e somar quando apropriado
        combined_df = combined_df.groupby(combined_df.index).sum(min_count=1)

        # Garantir que não haja repetição de índices
        combined_df = combined_df[~combined_df.index.duplicated(keep='first')]

        st.session_state['df_original'] = combined_df

        # Mensagem de sucesso
        st.success("Dados enviados para análise com sucesso!")
        return True
