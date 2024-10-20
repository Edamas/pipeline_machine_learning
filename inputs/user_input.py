import streamlit as st
import pandas as pd
from io import StringIO
import hashlib
from inputs.send_to_analysis import send_to_analysis

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

    # Instruções para o usuário
    with st.expander('Instruções', False):
        col_data, col_valor = st.columns(2)
        with col_data:
            st.markdown('''
                A primeira coluna do arquivo deve conter apenas datas.
                O formato de data deve ser consistente para todos os registros.
                Formatos aceitos incluem:
                - `dd/mm/aa`, `dd-mm-aa`
                - `dd/mm/aaaa`, `dd-mm-aaaa`
                - `mm/aaaa`, `mm/aa`
                - `aaaa`
            ''')
        with col_valor:
            st.markdown('''
                A segunda coluna deve conter valores numéricos. Tipos de valores aceitos incluem:
                - Identificadores de milhares, como `1.000` ou `1,000`
                - Separadores de vírgula para decimais, como `1.234,56`
                - Notação científica, como `1e6` para representar `1000000`
                - Números negativos, como `-1234,56`
                Se houver mais de uma coluna de valores, você será solicitado a escolher qual utilizar.
            ''')

    # Carregar arquivo
    file = st.file_uploader('Envie o arquivo (xls, xlsx, csv, tsv)', ['xls', 'xlsx', 'csv', 'tsv'], accept_multiple_files=False)
    if file:
        file_hash, content = load_file(file)
        nome = file.name
        extensao = nome.split('.')[-1].lower()
        st.success(f'`{nome}` carregado')
        st.write(f'Tipo: `{extensao}`')

        # Tratamento para arquivos CSV ou TSV
        if extensao in ['tsv', 'csv']:
            # Identificar separador automaticamente
            content = StringIO('\n'.join([line for line in content.decode("utf-8").splitlines() if line.strip()]))
            sep = ',' if extensao == 'csv' else '\t'
            try:
                df = pd.read_csv(content, sep=sep, thousands=',', quotechar='"', engine='python').dropna(how='all')
                st.write('Arquivo carregado com sucesso!')
            except Exception as e:
                st.error(f'Erro ao ler o arquivo: {e}')
                return

        # Tratamento para arquivos Excel
        elif extensao in ['xls', 'xlsx']:
            try:
                xls = pd.ExcelFile(file)
                sheets = xls.sheet_names
                if len(sheets) == 1:
                    sheet = sheets[0]
                else:
                    sheet = st.radio('Escolha a planilha a ser carregada:', sheets, key=file_hash)
                df = pd.read_excel(xls, sheet_name=sheet)
                st.write('Planilha carregada com sucesso!')
            except Exception as e:
                st.error(f'Erro ao ler o arquivo Excel: {e}')
                return

        # Verificar e converter campo de data
        if df.empty:
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
        if st.button('Enviar para análise', key=f"enviar_{file_hash}"):
            if send_to_analysis(df):
                st.success('Série temporal adicionada para análise com sucesso!')
            else:
                st.error('Erro ao enviar a série temporal para análise.')
    else:
        st.warning('Nenhum arquivo carregado.')

# Execução do programa
if __name__ == '__main__':
    user_input()
