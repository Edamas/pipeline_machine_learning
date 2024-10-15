# timeserie.py
import streamlit as st
import pandas as pd


# Função para gerar série temporal
def gerar_timeserie():
        df = st.session_state['df_ibge']
        unidade = df['Unidade de Medida'].drop_duplicates()
        if not unidade.empty:
            unidade = unidade.tolist()[0]
            unidade = f" ({unidade}) - "
            if unidade == ' () - ':
                unidade = ' - '
        else: 
            unidade = ' - '
        variavel = df['Variável'].drop_duplicates()
        variavel = variavel.tolist()[0]
        
        for nivel in ['Brasil', 'Grande Região', 'Unidade da Federação', 'Município']:
            if nivel in df.columns:
                localidade = df[nivel].drop_duplicates()
                localidade = localidade.tolist()[0]
                localidade = f'{localidade} - {localidade}'
                break
        
        classificacoes = []
        for column in df.columns:
            if column not in 'Nível Territorial	Unidade de Medida	Valor	Variável	Grande Região	Unidade da Federação	Município	Brasil	Semestre	Ano	Semestre	Trimestre	Trimestre Móvel	data'.split('\t') and '(Código)' not in column:
                classificacao = df[column].drop_duplicates()
                classificacao = classificacao.tolist()[0]
                classificacoes.append(f'{column} - {classificacao}')
        classificacoes = '; '.join(classificacoes)
        if not classificacoes:
            classificacoes = ''
        st.write(classificacoes)
        
        nome_coluna_valor = f'{variavel} {unidade} {classificacoes} {localidade}'
        
        # Prepara a série temporal
        timeserie_df = pd.DataFrame({
            'data': df['data'],
            nome_coluna_valor: pd.to_numeric(df['Valor'], errors='coerce')  # Usar o campo correto para valor
        })
        timeserie_df.set_index('data', inplace=True)
        
        return timeserie_df