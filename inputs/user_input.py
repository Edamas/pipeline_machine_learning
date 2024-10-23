import streamlit as st
import pandas as pd
import hashlib
from inputs.funcoes_user_input import exibir_instrucoes, get_str, get_excel

@st.cache_data(show_spinner=False)
def load_file(file):
    """
    Função para carregar e armazenar o arquivo no cache para evitar recarregamentos desnecessários.
    """
    content = file.getvalue()
    file_hash = hashlib.md5(content).hexdigest()
    return file_hash, content

# Função principal para entrada de série temporal
def user_input():
    st.title('Entrada de Série Temporal pelo Usuário')

    # Exibir instruções
    exibir_instrucoes()
    col0, col1, col2 = st.columns(3)
    
    with col0:
        # Carregar arquivo
        file = st.file_uploader('Envie o arquivo (xls, xlsx, csv, tsv, txt)', ['xls', 'xlsx', 'csv', 'tsv', 'txt'], accept_multiple_files=False)
    
    with col1:
        st.write(' ')
        st.write(' ')
        if file:
            file_hash, content = load_file(file)
            nome = file.name
            extensao = nome.split('.')[-1].lower()
            st.success(f'`{nome}` carregado')
        else:
            st.warning('Nenhum arquivo carregado')
    if file:
        # Tratamento para arquivos de texto
        if extensao in ['xls', 'xlsx']:
            with col2:
                st.write(' ')
                st.write(' ')
                df = get_excel(file)
        else:
            with col2:
                st.write(' ')
                st.write(' ')
                df = get_str(file, extensao)
    
        # Verificar e converter campo de data
        if df is None or df.empty:
            st.error('O DataFrame está vazio. Verifique o arquivo enviado.')
            return

        # Identificar automaticamente coluna de datas e valores
        colunas = df.columns.tolist()
        coluna_data = None
        for col in colunas:
            if df[col].astype(str).str.contains(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', regex=True).any():
                coluna_data = col
                break
        if not coluna_data:
            for col in colunas:
                if df[col].astype(str).str.match(r'\d{4}').any():
                    coluna_data = col
                    df[coluna_data] = pd.to_datetime(df[coluna_data].astype(str) + '-12-31', format='%Y-%m-%d', errors='coerce')
                    break

        # Se não encontrar automaticamente, perguntar ao usuário
        if not coluna_data:
            coluna_data = st.radio('Selecione a coluna de datas:', colunas, key=f"data_{file_hash}")

        colunas_valores = [col for col in colunas if col != coluna_data]
        
        if len(colunas_valores) == 0:
            st.error('Nenhuma coluna de valor identificada. Verifique o arquivo enviado.')
            return
        if len(colunas_valores) == 1:
            coluna_valor = colunas_valores[0]
        
        elif len(colunas_valores) > 1:
            coluna_valor = st.radio('Selecione a coluna de valores:', colunas_valores, key=f"valor_{file_hash}")

        # Tratar formato da coluna de data e converter para dd/mm/aaaa
        if coluna_data:
            if df[coluna_data].astype(str).str.match(r'\d{4}$').any():
                df[coluna_data] = pd.to_datetime(df[coluna_data].astype(str) + '-12-31', format='%Y-%m-%d', errors='coerce')
            else:
                df[coluna_data] = pd.to_datetime(df[coluna_data].apply(lambda x: str(x).strip() if pd.notnull(x) else x), errors='coerce')

            df[coluna_data] = df[coluna_data].dt.strftime('%d/%m/%Y')
            df.set_index(coluna_data, inplace=True)
            df.index.name = 'data'

        # Verificar e tratar valores não numéricos na coluna de valores
        df[coluna_valor] = df[coluna_valor].astype(str).str.strip().str.replace(',', '.', regex=False)

        df[coluna_valor] = pd.to_numeric(df[coluna_valor], errors='coerce')
        if df[coluna_valor].isna().all():
            st.error('Todos os valores da coluna selecionada são inválidos após a conversão. Verifique o arquivo enviado.')
            return
        
        df[coluna_valor] = df[coluna_valor].fillna(0)

        # Alterar nome da coluna de valores
        if coluna_valor == f'Valor_{1:02d}':
            contador = 1
            while f'Valor_{contador:02d}' in df.columns or f'Valor_{contador:02d}' in (st.session_state.get('df_original', pd.DataFrame()).columns):
                contador += 1
            novo_nome_valor = st.text_input('Nome da coluna de valores:', value=f'Valor_{contador:02d}', key=f"nome_coluna_{file_hash}")
        else:
            novo_nome_valor = st.text_input('Nome da coluna de valores:', value=coluna_valor, key=f"nome_coluna_{file_hash}")

        if novo_nome_valor in df.columns and novo_nome_valor in st.session_state.get('df_original', pd.DataFrame()).columns:
            st.warning(f'O nome da coluna "{novo_nome_valor}" já existe e será sobrescrito se não for alterado.')
        df.rename(columns={coluna_valor: novo_nome_valor}, inplace=True)

        # Apresentar DataFrame
        st.dataframe(df, use_container_width=True)

        # Botão para enviar para análise
        enviar = st.button('Enviar para análise', key=f"enviar_{nome}")
        if enviar:
            from inputs.send_to_analysis import send_to_analysis
            if send_to_analysis(df):
                st.success('Série temporal adicionada para análise com sucesso!')
            else:
                st.error('Erro ao enviar a série temporal para análise.')

# Execução do programa
if __name__ == '__main__':
    user_input()
