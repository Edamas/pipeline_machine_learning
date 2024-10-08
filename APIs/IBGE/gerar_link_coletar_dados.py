import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

def gerar_link():
    
    base_url = "https://servicodados.ibge.gov.br/api/v3/agregados"
    # Constrói o link com os parâmetros fornecidos
    parametros = st.session_state['parametros_ibge']
    
    url = f'https://apisidra.ibge.gov.br/values'
    url += f'/t/{parametros['codigo_tabela']}'
    url += f'/v/{parametros['variavel']}'
    url += f'/{parametros['nivel']}/{parametros['localidade']}'
    
    # Verificar se as classificações estão em formato de lista e processá-las corretamente
    classificacoes = parametros['classificacoes']
    if isinstance(classificacoes, list):
        for cod_classificacao, cod_subclassificacao in classificacoes:
            url += f"/c{cod_classificacao}/{cod_subclassificacao}"
    
    url += '/p/all'  # todos os períodos
    url += '?formato=json'
    
    return url


def coletar_dados(url):
    with st.spinner(f"Coletando dados da série temporal..."):
        # Coletar os dados do link gerado
        try:
            response = requests.get(url)
            response.raise_for_status()  # Verifica se houve erro HTTP
        except Exception as e:
            st.error(f'Erro ao coletar dados de {url}. Erro: {e}')
            return pd.DataFrame()  # Retorna DataFrame vazio em caso de erro
        
        if response.status_code == 200:
            dados_json = response.json()

            # Passar codigo_tabela para obter_nome_periodo
            nome_periodo = obter_nome_periodo(st.session_state['parametros_ibge']['codigo_tabela'])  # Passando o codigo_tabela
            
            # Processar os dados, passando o nome do período
            df_dados = processar_dados(dados_json, nome_periodo)  # Passando nome_periodo
            
            return df_dados
        else:
            st.error("Erro ao coletar dados.")
            return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro


def obter_nome_periodo(codigo_tabela):
    """
    Acessa a página de consulta do SIDRA e identifica o nome do período (ex: 'Ano (Código)', 'Semestral (Código)').
    """
    url_consulta = f"https://apisidra.ibge.gov.br/desctabapi.aspx?c={codigo_tabela}"
    
    try:
        response = requests.get(url_consulta)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Localiza o nome do período na página (como 'Ano (Código)', 'Semestral (Código)')
        periodo_tag = soup.find('span', {'id': 'lblNomePeriodo'})
        
        if periodo_tag:
            nome_periodo = periodo_tag.text.strip().split('(')[0].strip()  # Extrai o nome do período
            return nome_periodo
        else:
            st.error("Não foi possível encontrar o nome do período na página.")
            return None

    except Exception as e:
        st.error(f"Erro ao acessar a página de consulta: {e}")
        return None

def processar_dados(response_json, nome_periodo):
    """
    Processa o JSON retornado pela API do SIDRA, identifica a coluna de período correta, e ajusta os dados.
    """
    
    # A primeira linha do JSON contém os cabeçalhos corretos
    colunas = response_json[0]  # A primeira linha contém os nomes das colunas descritivas
    
    # As linhas subsequentes são os dados reais
    dados = response_json[1:]  # O restante do JSON são os dados
    
    # Criar o DataFrame com os dados
    df_dados = pd.DataFrame(dados)
    
    # Renomear as colunas usando os valores da primeira linha do JSON
    df_dados.columns = list(colunas.values())  # Renomeia as colunas com os cabeçalhos descritivos
    
    nome_periodo = nome_periodo + ' (Código)'
    # Agora podemos identificar a coluna que corresponde ao período (ex: 'Ano (Código)', 'Semestral (Código)')
    if nome_periodo in df_dados.columns:
        # Processar a coluna de datas com base no período identificado
        if df_dados[nome_periodo].str.len().max() == 6:  # Exemplo: Ano e Mês
            df_dados['data'] = pd.to_datetime(df_dados[nome_periodo], format='%Y%m')
            df_dados['data'] += pd.offsets.MonthEnd(0)  # Ajusta para o último dia do mês
            df_dados['data'] = df_dados['data'].dt.strftime('%d/%m/%Y')  # Formata em dd/mm/aaaa
        elif df_dados[nome_periodo].str.len().max() == 4:  # Exemplo: Apenas Ano
            df_dados['data'] = pd.to_datetime(df_dados[nome_periodo], format='%Y')
            df_dados['data'] += pd.offsets.YearEnd(0)  # Ajusta para o último dia do ano
            df_dados['data'] = df_dados['data'].dt.strftime('%d/%m/%Y')  # Formata em dd/mm/aaaa
        else:
            st.error("Formato de data desconhecido.")
            return pd.DataFrame()
        return df_dados

    else:
        st.error(f"Coluna de período '{nome_periodo}' não encontrada no DataFrame.")
        return pd.DataFrame()