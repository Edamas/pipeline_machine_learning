import streamlit as st
import pandas as pd
import re
from io import StringIO

def exibir_instrucoes():
    """
    Função para exibir as instruções na interface do Streamlit.
    """
    with st.expander('Instruções', False):
        col_data, col_valor, col_geral = st.columns([3, 3, 1])
        with col_data:
            st.markdown('''
                ### Datas
                Como este projeto trata de séries temporais, a primeira coluna do arquivo deve conter apenas datas.
                
                O formato de data deve ser consistente para todos os registros.
                
                ##### Formatos aceitos incluem:
                
                Datas completas:
                >- `dd/mm/aaaa` (padrão)
                >- `dd-mm-aaaa`
                >- `dd/mm/aa`
                >- `dd-mm-aa`
                
                Se só houver o mês e ano, sem especificação do dia, por padrão, data será convertida para o último dia daquele mês e ano (exemplo: `08/20` se tornará `31/08/2020`)
                >- `mm/aaaa`
                >- `mm/aa`
                
                Será convertido para o último dia do ano:
                >- `aaaa` 
            ''')
        with col_valor:
            st.markdown('''
                ### Valores
                
                A segunda coluna deve conter valores numéricos.
                
                Se houver mais de uma coluna de valores, você será solicitado a escolher qual enviará para análise/processamento.
                
                ##### Tipos de valores aceitos incluem:
                > - Identificadores de milhares, como `1.000` ou `1,000`
                
                ##### Separadores decimais:
                >- vírgula: `1.234,56` ou `1234,56`
                >- ponto: `1,234.56` ou `1234.56`
                >- Números negativos, como `-1,234.56`, `-1.234,56`, `-1234,56` ou `-1234.56`
                
                ##### Limites de tamanho dos números:
                >- valores devem ser menores que `+2^53`.
                >- valores devem ser maiores que `-2^53`.
                
                ##### Moeda
                Não são aceitos caracteres de moeda, como `BRL`, `USD`, `R$`, `US$`, `BTC`, etc.
            ''')
        with col_geral:
            st.markdown('''
                ### Arquivos
                
                ##### Arquivos aceitos:
                >- `.xls`
                >- `.xlsx`
                >- `.csv`
                >- `.tsv`
                >- `.txt`
                
                ##### Separadores de colunas:
                - Tabulação (`\\t`)
                - vírgula (`,`)
                - ponto e vírgula (`;`)
                - barra vertical (`|`).
                
                ##### Quebra de linha:
                - Enter - padrão (`\\n`)
                
                ##### Codificação (encoding):
                - `utf-8`
            ''')

def get_str(file, extensao):
    """
    Função para processar arquivos de texto (csv, tsv, txt) e retornar um DataFrame.
    """
    content = file.getvalue().decode("utf-8")
    content_str = StringIO(content)

    while '\r' in content or '\n\n' in content or ' \n' in content or '\n '  in content or ' \t' in content or  '\t ' in content:
        content = content.strip().replace('\r\n', '\n')
        content = content.strip().replace('\r', '\n')
        content = content.strip().replace('\n\n', '\n')
        content = content.strip().replace(' \n', '\n')
        content = content.strip().replace('\n ', '\n')
        content = content.strip().replace(' \t', '\t')
        content = content.strip().replace('\t ', '\t')

    # Tentativa de identificar separador para arquivos txt
    sep = re.findall(r'[;|\t,]', content.split('\n')[1])
    
    if sep:
        sep = sep[0]
    else:
        sep = st.text_input('Separador de colunas não identificado. Favor especificar o caractere de separador', value=',')

    if sep:
        valores = {}
        colunas = {}
        for num_linha, linha in enumerate(content.split('\n')):
            if not linha.strip():
                continue
            linha = linha.split(sep)
            #cabeçalho
            if num_linha == 0:
                primeiro_caractere_da_primeira_linha = linha[0][0]
                e_numerico = primeiro_caractere_da_primeira_linha.isnumeric()
                if e_numerico:  # o primeiro dígito da primeira linha é numérico (data)
                    st.warning('A primeira linha contém valores numéricos. É necessário nomear os campos antes de adicionar valores')
                    for numero_coluna, valor in enumerate(linha):
                        if numero_coluna == 0:
                            valores['data'] = [valor]
                            colunas['data'] = {'max_virgulas': 0, 'max_pontos': 0, 'exemplo': None, 'negativo': None, 'moeda': None}
                        else:
                            titulo_coluna = st.text_input(f'Digite o Título da Coluna número: `{numero_coluna}` (cujo primeiro valor é "{valor}")', value=f"Valores_{numero_coluna}")
                            valores[titulo_coluna] = [valor]
                            colunas[titulo_coluna] = {'max_virgulas': valor.count(','), 'max_pontos': valor.count('.'), 'exemplo': valor, 'negativo': '-' in valor, 'moeda': False}
                
                else:  # o primeiro dígito da primeira linha é alfa (cabeçalho)
                    for indice_coluna, titulo_coluna in enumerate(linha):
                        if indice_coluna == 0:
                            valores['data'] = []
                            colunas['data'] = {'max_virgulas': 0, 'max_pontos': 0, 'exemplo': None, 'negativo': False, 'moeda': False}
                        else:
                            valores[titulo_coluna] = []
                            colunas[titulo_coluna] = {'max_virgulas': 0, 'max_pontos': 0, 'exemplo': None, 'negativo': False, 'moeda': False}
            # linhas
            else:
                for numero_coluna, valor in enumerate(linha):
                    for indice_coluna, coluna in enumerate(colunas):
                        if indice_coluna == numero_coluna:
                            if indice_coluna == 0:
                                coluna = 'data'
                            valor = valor.strip()
                            virgulas = valor.count(',')
                            pontos = valor.count('.')
                            negativo = '-' in valor
                            if colunas[coluna]['max_virgulas'] < virgulas:
                                colunas[coluna]['max_virgulas'] = virgulas
                            if colunas[coluna]['max_pontos'] < pontos:
                                colunas[coluna]['max_pontos'] = pontos
                            if negativo:
                                colunas[coluna]['negativo'] = True
                            if not colunas[coluna]['exemplo']:
                                colunas[coluna]['exemplo'] = valor
                            elif len(colunas[coluna]['exemplo']) < len(valor):
                                colunas[coluna]['exemplo'] = valor
                            valores[coluna].append(valor)
        for coluna in colunas:
            if coluna != 'data':
                virgulas = colunas[coluna]['max_virgulas']
                pontos = colunas[coluna]['max_pontos']
                exemplo = colunas[coluna]['exemplo']
                
                if sep == ',':
                    # vírgula só funciona se houver delimitador de texto
                    pass
                if "'" in exemplo:
                    quotechar = "'"
                elif '"' in exemplo:
                    quotechar = '"'
                else:
                    quotechar = None
                if virgulas == 0:
                    # sem vírgulas - pode ser thousands, decimal ou nenhum
                    if pontos == 0:
                        # sem vírgula, sem pontos - provavelmente padrão
                        thousands = '.'
                        decimal = ','
                    elif pontos == 1:
                        # sem vírgula, com 1 ponto - pode ser decimal ou thousands:
                        if 5 >= len(exemplo) >= 7: # thousands: de 1.000 a 999.999 (podem ser decimais (preferência por vírgula como decimal))
                            if exemplo[-4] == '.':  
                                thousands = '.'
                                decimal = ','
                            else:
                                thousands = ','
                                decimal = '.'
                        else:
                            thousands = ','
                            decimal = '.'
                    elif pontos > 1:
                        # sem vírgulas, com mais de um ponto - ponto é thousands
                        thousands = '.'
                        decimal = ','
                elif virgulas == 1:
                    # uma vírgula - pode ser thousands ou decimal
                    if pontos == 0:
                        # uma vírgula, sem pontos - ambos podem ser decimal ou thousands
                        if 5 >= len(exemplo.replace('"', '')) >= 7: # thousands: de 1.000 a 999.999 (podem ser decimais)
                            if exemplo.replace('"', '')[-4] == ',':  # se o ponto for a quarta casa, do fim para o começo, a vírgula é thousands
                                thousands = ','
                                decimal = '.'
                            else:  # caso contrário, a vírgula é decimal
                                thousands = '.'
                                decimal = ','
                        else:  # caso o número tenha vírgula, mas não esteja entre 1.000 e 999.999, a vírgula é decimal
                            thousands = '.'
                            decimal = ','
                    elif pontos == 1:
                        # uma vírgula, um ponto - ambos podem ser decimal ou thousands
                        if exemplo.replace('"', '').index(',') < exemplo.replace('"', '').index('.'):  # a vírgula é thousands se vem antes do ponto, que é decimal
                            thousands = ','
                            decimal = '.'
                        else:  # a vírgula é thousands se vem antes do ponto, que é decimal
                            thousands = '.'
                            decimal = ','
                    elif pontos > 1:
                        # uma vírgula, com mais de um ponto - ponto é thousands, vírgula é decimal
                        thousands = '.'
                        decimal = ','
                elif virgulas > 1:
                    # mais de uma vírgula - é thousands, não é decimal
                    if pontos in  [0, 1]:  # OK
                        # mais de uma vírgula, com um ou sem pontos - ponto é decimal
                        thousands = ','
                        decimal = '.'
                    elif pontos > 1: 
                        # mais de uma vírgula, mais de um ponto - erro
                        if pontos > virgulas:  # há mais pontos que vírgulas, provavelmente pontos é thousands, vírgula é decimal
                            thousands = '.'
                            decimal = ','
                        else:  # o número de vírgulas é maior ou igual ao de pontos, vírgulas é thousands, ponto é decimal (preferência por vírgula como decimal)
                            thousands = ','
                            decimal = '.'
                        
                        st.error('Valores com mais de um ponto e com mais de uma vírgula, simultaneamente. Favor corrigir o(s) valor(es) no arquivo')
                else:
                    st.error('Número de vírgulas não é 0 ou mais')
        valores_final = {}
        for coluna in valores:
            if coluna not in valores_final:
                valores_final[coluna] = []
            for v in valores[coluna]:
                v = v.replace(thousands, '').strip()
                v = v.replace(decimal, '.')
                if '.' in v:
                    v = float(v)
                else:
                    v = int(v)
                valores_final[coluna].append(v)
        # resumo da identificação
        with st.expander('Resumo da identificação dos dados', expanded=False):
            st.write(f'Tipo: `{extensao}`')
            st.write(f'Separador de linhas: `\\n [caractere de quebra de linha]`')
            st.write(f'Separador de colunas: `{sep if sep != '\t' else '\\t [caractere de tabulação]'}`')
            st.write(f'Número de Colunas: {len(colunas)}')
            st.write(f'Separador Decimal: `{decimal}`')
            st.write(f'Separador de milhar: `{thousands}`')
            st.write(f'Delimitador de valores: `{quotechar}`')
        df = pd.DataFrame()
        for col in valores_final:
            df[col] = valores_final[col]
        
        return df


def get_excel(file):
    """
    Função para processar arquivos Excel e retornar um DataFrame.
    """
    try:
        xls = pd.ExcelFile(file)
        sheets = xls.sheet_names
        if len(sheets) == 1:
            sheet = sheets[0]
        else:
            sheet = st.radio('Escolha a planilha a ser carregada:', sheets, key=file.name)
        df = pd.read_excel(xls, sheet_name=sheet)
        return df
    except Exception as e:
        st.error(f'Erro ao ler o arquivo Excel: {e}')
        return None
