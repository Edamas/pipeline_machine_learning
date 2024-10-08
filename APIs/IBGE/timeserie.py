# timeserie.py
import streamlit as st
import pandas as pd


# Função para gerar série temporal
def gerar_timeserie():
        df = st.session_state['df_ibge']
        unidade = f" ({df['Unidade de Medida'].drop_duplicates()[0]}) - "
        if unidade == ' () - ':
            unidade = ' - '
        
        variavel = df['Variável'].drop_duplicates()[0]
        for nivel in ['Brasil', 'Grande Região', 'Unidade da Federação', 'Município']:
            if nivel in df.columns:
                localidade = df[nivel].drop_duplicates()
                localidade = f'{localidade.name} - {localidade.values[0]}'
                break
        
        nome_coluna_valor = f'{variavel}{unidade}{localidade}'
        
        # Prepara a série temporal
        timeserie_df = pd.DataFrame({
            'data': df['data'],
            nome_coluna_valor: pd.to_numeric(df['Valor'], errors='coerce')  # Usar o campo correto para valor
        })
        timeserie_df.set_index('data', inplace=True)
        
        return timeserie_df