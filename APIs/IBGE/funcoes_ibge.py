import requests, os
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import time 

# Função para carregar os dados dos arquivos CSV e metadados
def carregar_dados():
    base_dir = os.path.join('APIs', 'IBGE')  # Diretório base para os arquivos
    arquivos = {
        'df_metadados': 'metadados_tabelas.csv',
        'df_niveis': 'niveis_geograficos.csv',
        'df_periodicidade': 'periodicidade.csv',
        'df_periodos': 'periodos.csv',
        'df_classificacoes': 'classificacoes.csv',
        'df_subclassificacoes': 'subclassificacoes.csv',
        'df_variaveis': 'variaveis.csv',
        'rel_tabelaXniveis': 'tabela_x_niveis.csv',
        'rel_tabelaXperiodicidade': 'tabela_x_periodicidade.csv',
        'rel_tabelaXperiodos': 'tabela_x_periodos.csv',
        'rel_tabelaXclassificacoes': 'tabela_x_classificacoes.csv',
        'rel_tabelaXsubclassificacoes': 'tabela_x_subclassificacoes.csv',
        'rel_tabelaXvariaveis': 'tabela_x_variaveis.csv',
    }
    for key, file in arquivos.items():
        file_path = os.path.join(base_dir, file)
        if key == 'df_metadados':
            st.session_state[key] = pd.read_csv(file_path, sep='\t', index_col='Número', encoding='utf-8')
        else:
            st.session_state[key] = pd.read_csv(file_path, sep='\t', encoding='utf-8')
        
        # Inicializar o número total e filtrado de registros para cada DataFrame
        st.session_state[f'{key}_total'] = len(st.session_state[key])
        st.session_state[f'{key}_filtrado'] = len(st.session_state[key])

# Função para criar dataframes selecionáveis e armazenar o número de registros filtrados
def criar_dataframe_selecionavel(df, titulo, descricao, df_key, col=None, hide_index=False):
    titulo = f"**{titulo}**: {descricao}"
    if col:
        col.write(titulo)
        event = col.dataframe(df, use_container_width=True, hide_index=hide_index, on_select="rerun", selection_mode="single-row")
    else:
        st.write(titulo)
        event = st.dataframe(df, use_container_width=True, hide_index=hide_index, on_select="rerun", selection_mode="single-row")
    
    # Armazena o número de registros filtrados
    st.session_state[f'{df_key}_filtrado'] = len(df)
    if 'selection' in event:
        if 'rows' in event['selection']:
            if event['selection']['rows']:
                return event['selection']["rows"]
    return []


# Função para aplicar os filtros de código de tabela a qualquer DataFrame solicitado
def aplicar_filtro_por_codigos_tabelas(df_key, codigos_selecionados):
    """
    Aplica o filtro de código de tabela no DataFrame especificado.
    
    Parâmetros:
        df_key: Nome da tabela no session_state (chave) que será filtrada.
        codigos_selecionados: Lista de códigos de tabela a serem usados como filtro.
    """
    if len(codigos_selecionados) > 0:
        if st.session_state[df_key].index.isin(codigos_selecionados).any():
            st.session_state[df_key] = st.session_state[df_key][st.session_state[df_key].index.isin(codigos_selecionados)]
            # Atualiza o número de registros filtrados
            st.session_state[f'{df_key}_filtrado'] = len(st.session_state[df_key])
        else:
            st.write(f'O índice "Código Tabela" não foi encontrado no DataFrame {df_key}')
    else:
        st.warning(f'Nenhum código de tabela foi selecionado para filtrar a tabela {df_key}.')


# Função para obter descrições da tabela
def obter_descricao_tabela(codigo_tabela):
    url = f"https://apisidra.ibge.gov.br/desctabapi.aspx?c={codigo_tabela}"
    try:
        response = requests.get(url)
    except ConnectionError:
        try:
            response = requests.get(url)
        except Exception as e:
                st.error(f'Erro de conexão com {url}. Verifique sua conexão ou tente novamente. Erro: {e}')

    # Verifique se a resposta tem conteúdo
    if response.status_code == 200 and response.content:
        try:
            # Tentativa de decodificar a resposta como JSON
            dados_json = response.json()
            descricao = {
                'Código Tabela': dados_json['tabela']['codigo'],
                'Nome Tabela': dados_json['tabela']['nome'],
                'Pesquisa': dados_json['tabela']['pesquisa'],
                'Assunto': dados_json['tabela']['assunto'],
                'Última Atualização': dados_json['tabela']['atualizacao'],
                'Nota': dados_json['tabela']['nota'],
                'Fonte': dados_json['tabela']['fonte']
            }
            return descricao
        except ValueError:
            # Caso a resposta não seja JSON, exiba o conteúdo da resposta para depuração
            st.error(f"Erro ao decodificar a resposta da API para a tabela {codigo_tabela}. Resposta: {response.content.decode('utf-8')}")
            return None
    else:
        st.error(f"Erro ao consultar a tabela {codigo_tabela}. Status: {response.status_code}")
        return None


# Função para obter classificações e subclassificações da tabela
def obter_classificacoes_subclassificacoes(codigo_tabela):
    url = f"https://apisidra.ibge.gov.br/desctabapi.aspx?c={codigo_tabela}"
    try:
        response = requests.get(url)
    except ConnectionError:
        try:
            response = requests.get(url)
        except Exception as e:
                st.error(f'Erro de conexão com {url}. Verifique sua conexão ou tente novamente. Erro: {e}')

    if response.status_code != 200:
        st.error(f"Erro ao acessar as classificações da tabela {codigo_tabela}.")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    dimensoes = []
    classificacoes = soup.find_all('span', id=lambda x: x and x.startswith('lstClassificacoes_lblIdClassificacao'))

    for classificacao in classificacoes:
        dimensao_codigo = classificacao.text
        dimensao_nome = classificacao.find_next('span', {'class': 'tituloLinha'}).text
        subitens = []
        subitens_elements = classificacao.find_next('table').find_all('tr')

        for subitem_element in subitens_elements:
            subitem_codigo = subitem_element.find('span', style='color:Red').text
            subitem_nome = subitem_element.find_next('span', id=lambda x: x and 'lblNomeCategoria' in x).text
            subitens.append({'Código': subitem_codigo, 'Nome': subitem_nome})

        dimensoes.append({'Dimensão': dimensao_nome, 'Código': dimensao_codigo, 'Subitens': subitens})

    return dimensoes


# Função para exibir classificações e subclassificações em colunas separadas
def exibir_classificacoes_subclassificacoes(classificacoes):
    selecoes_classificacoes = []

    for idx, classificacao in enumerate(classificacoes):
        if 'Subitens' in classificacao and classificacao['Subitens']:
            df_subclassificacoes = pd.DataFrame(classificacao['Subitens'])
            
            # Usa a função criar_dataframe_selecionavel para capturar a seleção do usuário
            selecao = criar_dataframe_selecionavel(
                df_subclassificacoes,
                f"Classificação: {classificacao['Dimensão']}",
                "Selecione a Subclassificação",
                f"subclass_{classificacao['Código']}",
            )
            
            # Certifique-se de que a seleção foi feita corretamente
            if selecao:
                subclass_selecionada = df_subclassificacoes.iloc[selecao[0]]  # Seleciona a subclassificação
                selecoes_classificacoes.append({
                    'Código Classificação': classificacao['Código'],
                    'Código Subclassificação': subclass_selecionada['Código']
                })
    
    return selecoes_classificacoes


# Função para obter níveis territoriais e localidades a partir do link da tabela
def selecionar_niveis_localidades(codigo_tabela):
    # Obter e apresentar níveis territoriais
    url = f"https://apisidra.ibge.gov.br/desctabapi.aspx?c={codigo_tabela}"
    with st.spinner(f"Coletando dados dos níveis territoriais..."):
        try:
            response = requests.get(url)
        except ConnectionError:
            try:
                response = requests.get(url)
            except Exception as e:
                st.error(f'Erro de conexão com {url}. Verifique sua conexão ou tente novamente. Erro: {e}')
        soup = BeautifulSoup(response.content, 'html.parser')
        niveis_territoriais = soup.find_all('span', id=lambda x: x and x.startswith('lstNiveisTerritoriais_lblNomeNivelterritorial'))
    niveis_list = []
    
    for i, nivel_nome in enumerate(niveis_territoriais):
        nivel_codigo_span = soup.find('span', id=f'lstNiveisTerritoriais_lblIdNivelterritorial_{i}')
        nivel_codigo = nivel_codigo_span.text.strip()
        niveis_list.append({'Código Nível': nivel_codigo, 'Nome Nível': nivel_nome.text.strip()})
    
    niveis_df = pd.DataFrame(niveis_list)
    
    if niveis_df.empty:
        st.error("Nenhum nível territorial encontrado.")
        return None, None

    # Exibir DataFrame selecionável para nível territorial
    nivel_idx = criar_dataframe_selecionavel(niveis_df, 'Níveis Territoriais', 'Selecione apenas um Nível Territorial', 'df_niveis')
    if not nivel_idx:
        return None, None

    nivel = niveis_df['Código Nível'][nivel_idx].tolist()[0]

    # Obter localidades para o nível territorial selecionado
    if nivel:
        with st.spinner(f"Coletando dados das localidades..."):
            url_localidades = f"https://apisidra.ibge.gov.br/LisUnitTabAPI.aspx?c={codigo_tabela}&n={nivel}&i=P"
            
            try:
                df_localidades = pd.read_html(url_localidades)[1]  # Carregar a tabela de localidades
            except:
                try:
                    df_localidades = pd.read_html(url_localidades)[1]
                except Exception as e:
                    st.error(f'Erro ao coletar a tabela {url_localidades}: {e}')
            
            if df_localidades.empty:
                st.error("Nenhuma localidade encontrada.")
                return nivel, None, None

            # Exibir DataFrame selecionável para localidade
            df_localidades.index = df_localidades['Código']
            del df_localidades['Código']
            localidade_idx = criar_dataframe_selecionavel(df_localidades, 'Localidades', 'Selecione apenas uma Localidade', 'df_localidades')
            
            if not localidade_idx:
                return nivel, None, None
            
            localidade = df_localidades.iloc[localidade_idx].index.values[0]
            return nivel, localidade, df_localidades

    return None, None


# Função para formatar datas
def formatar_datas(periodo):
    if len(str(periodo)) == 4:  # Caso venha apenas o ano
        return f"31/12/{periodo}"
    elif len(str(periodo)) == 6:  # Caso venha no formato aaaamm
        ano = periodo[:4]
        mes = periodo[4:]
        ultimo_dia = pd.Period(f"{ano}-{mes}", 'M').end_time.day  # Último dia do mês
        return f"{ultimo_dia}/{mes}/{ano}"


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
            st.write(f"Período identificado: {nome_periodo}")
            return nome_periodo
        else:
            st.error("Não foi possível encontrar o nome do período na página.")
            return None

    except Exception as e:
        st.error(f"Erro ao acessar a página de consulta: {e}")
        return None


# USADO
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
    
    st.write("DataFrame após renomeio das colunas:")
    st.dataframe(df_dados)
    nome_periodo = nome_periodo + ' (Código)'
    st.write(nome_periodo)
    # Agora podemos identificar a coluna que corresponde ao período (ex: 'Ano (Código)', 'Semestral (Código)')
    if nome_periodo in df_dados.columns:
        # Processar a coluna de datas com base no período identificado
        if df_dados[nome_periodo].str.len().max() == 6:  # Exemplo: Ano e Mês
            df_dados['data'] = pd.to_datetime(df_dados[nome_periodo], format='%Y%m')
        elif df_dados[nome_periodo].str.len().max() == 4:  # Exemplo: Apenas Ano
            df_dados['data'] = pd.to_datetime(df_dados[nome_periodo], format='%Y')
        else:
            st.error("Formato de data desconhecido.")
            return pd.DataFrame()
        
        # Converte a coluna de valor para numérico, se existir
        if 'Valor' in df_dados.columns:
            df_dados['Valor'] = pd.to_numeric(df_dados['Valor'], errors='coerce')  # Converte valores para numérico
        else:
            st.error("Coluna 'Valor' não encontrada no JSON.")
            return pd.DataFrame()

        # Remover linhas com valores nulos nas colunas de data e valor
        df_dados.dropna(subset=['data', 'Valor'], inplace=True)

        st.write(f"Número de linhas após o processamento: {len(df_dados)}")
        return df_dados

    else:
        st.error(f"Coluna de período '{nome_periodo}' não encontrada no DataFrame.")
        return pd.DataFrame()

# Função para obter variáveis da tabela
def obter_variaveis(codigo_tabela):
    url = f"https://apisidra.ibge.gov.br/desctabapi.aspx?c={codigo_tabela}"
    try:
        response = requests.get(url)
    except ConnectionError:
        try:
            response = requests.get(url)
        except Exception as e:
                st.error(f'Erro de conexão com {url}. Verifique sua conexão ou tente novamente. Erro: {e}')

    if response.status_code != 200:
        st.error(f"Erro ao acessar a descrição da tabela {codigo_tabela}.")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    variaveis = []
    variaveis_elements = soup.find_all('span', id=lambda x: x and x.startswith('lstVariaveis_lblIdVariavel'))

    for variavel in variaveis_elements:
        codigo_variavel = variavel.text
        nome_variavel = variavel.find_next('span').text
        variaveis.append({'Código Variável': codigo_variavel, 'Nome Variável': nome_variavel})
    
    return variaveis


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
            codigo_tabela = st.session_state['codigo_tabela']
            nome_periodo = obter_nome_periodo(codigo_tabela)  # Passando o codigo_tabela

            # Processar os dados, passando o nome do período
            df_dados = processar_dados(dados_json, nome_periodo)  # Passando nome_periodo

            return df_dados
        else:
            st.error("Erro ao coletar dados.")
            return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro


def gerar_timeserie(df):
    try:
        # Verificar se a coluna 'Valor' existe no DataFrame
        if 'Valor' not in df.columns:
            st.error("A coluna 'Valor' não foi encontrada no DataFrame.")
            st.write("Colunas disponíveis:", df.columns)
            return pd.DataFrame()  # Retorna um DataFrame vazio se não encontrar

        # Verificar se a coluna de data existe
        if 'data' not in df.columns:
            st.error("A coluna 'data' não foi encontrada no DataFrame.")
            return pd.DataFrame()  # Retorna um DataFrame vazio se não encontrar

        # Tentar converter a coluna de data para datetime, considerando os formatos possíveis
        df['data'] = pd.to_datetime(df['data'], errors='coerce', format='%Y-%m-%d')  # Exemplo de formato

        # Verifica se houve erros na conversão
        if df['data'].isnull().any():
            st.error("Formato de data desconhecido ou inválido. Verifique os dados coletados.")
            st.write(df['data'].head())  # Exibe as primeiras linhas da coluna de data para depuração
            return pd.DataFrame()  # Retorna um DataFrame vazio se encontrar erros na data

        # Prepara a série temporal
        timeserie_df = pd.DataFrame({
            'data': df['data'],
            'Valor': pd.to_numeric(df['Valor'], errors='coerce')  # Usar o campo correto para valor
        })

        # Remove valores nulos
        timeserie_df.dropna(inplace=True)

        return timeserie_df

    except KeyError as e:
        st.error(f"Chave não encontrada: {e}")
        return pd.DataFrame()



def construir_link_unico(tabela, variavel, classificacoes, nivel_territorial, localidade):
    # Iniciar a URL com a tabela
    url = f'https://apisidra.ibge.gov.br/values/t/{tabela}'

    # Adicionar o nível territorial e a localidade
    url += f'/n{nivel_territorial}/{localidade}'

    # Adicionar o período (todos os períodos)
    url += '/p/all'

    # Verificar se as classificações estão em formato de lista e processá-las corretamente
    if isinstance(classificacoes, list):
        for classificacao in classificacoes:
            if isinstance(classificacao, dict) and 'Código Classificação' in classificacao and 'Código Subclassificação' in classificacao:
                # Adicionar as classificações e subclassificações ao link
                url += f"/c{classificacao['Código Classificação']}/{classificacao['Código Subclassificação']}"

    # Adicionar a variável
    url += f'/v/{variavel["Código Variável"]}'

    # Adicionar o formato (json)
    url += '?formato=json'

    return url