import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from datetime import datetime

# Função para carregar os dados dos arquivos CSV e metadados
def carregar_dados():
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
        file = 'APIs/IBGE/' + file
        if key == 'df_metadados':
            st.session_state[key] = pd.read_csv(file, sep='\t', index_col='Código Tabela', encoding='utf-8')
            
        else:
            st.session_state[key] = pd.read_csv(file, sep='\t', encoding='utf-8')
        
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
    selecao = event.selection["rows"] if event else []
    return selecao


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


# Função para processar os dados e usar a primeira linha como cabeçalho
def processar_dados(response_json):
    # A primeira linha será usada como cabeçalho
    colunas = response_json[0]  # A primeira linha contém os cabeçalhos
    
    dados = response_json[1:]  # As linhas subsequentes são os dados
    # Criar DataFrame com os dados e os cabeçalhos obtidos
    df_dados = pd.DataFrame(dados, columns=colunas)
    df_dados.columns = list(colunas.values())
    # Formatar as datas para o último dia do período e no formato dd/mm/aaaa
    if 'Período' in df_dados.columns:
        df_dados['Período'] = df_dados['Período'].apply(formatar_datas)

    return df_dados


# Função principal para gerar o link e coletar os dados
def gerar_link_coletar_dados(codigo_tabela, variavel, classificacoes, nivel, localidade):
    url = construir_link_unico(codigo_tabela, variavel, classificacoes, nivel, localidade)
    
    st.write("Link Final Gerado:")
    st.write(url)

    # Coletar os dados do link gerado
    try:
        response = requests.get(url)
    except ConnectionError:
        try:
            response = requests.get(url)
        except Exception as e:
                st.error(f'Erro de conexão com {url}. Verifique sua conexão ou tente novamente. Erro: {e}')
    if response.status_code == 200:
        dados_json = response.json()

        # Processar os dados para usar a primeira linha como cabeçalho
        df_dados = processar_dados(dados_json)
        return df_dados
    else:
        st.error("Erro ao coletar dados.")
        

# Função para criar o link correto com as classificações, dimensões, nível, localidade e tabela
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

# Função principal para gerar o link e coletar os dados
def gerar_link_coletar_dados(codigo_tabela, variavel, classificacoes, nivel, localidade):
    url = construir_link_unico(codigo_tabela, variavel, classificacoes, nivel, localidade)
    
    st.write("Link Final Gerado:")
    st.write(url)

    with st.spinner(f"Coletando dados da série temporal..."):
        # Coletar os dados do link gerado
        try:
            response = requests.get(url)
        except ConnectionError:
            try:
                response = requests.get(url)
            except Exception as e:
                st.error(f'Erro de conexão com {url}. Verifique sua conexão ou tente novamente. Erro: {e}')
        
        if response.status_code == 200:
            dados_json = response.json()

            # Processar os dados para usar a primeira linha como cabeçalho
            df_dados = processar_dados(dados_json)
            return df_dados

        else:
            st.error("Erro ao coletar dados.")


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



def gerar_timeserie(df):
    # URL de consulta da tabela
    codigo_tabela = st.session_state['parametros_ibge']['codigo_tabela']
    nome_tabela = st.session_state['parametros_ibge']['nome_tabela']
    variavel = st.session_state['parametros_ibge']['variavel']
    nivel = st.session_state['parametros_ibge']['nivel']
    localidade = st.session_state['parametros_ibge']['localidade']

    url_consulta = f"https://apisidra.ibge.gov.br/desctabapi.aspx?c={codigo_tabela}"
    st.write(df)
    # Realiza a requisição dos dados
    response = requests.get(url_consulta)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Identificar a periodicidade a partir do HTML da página
    periodicidade_tag = soup.find('span', {'id': 'lblNomePeriodo'})
    if periodicidade_tag:
        periodicidade = periodicidade_tag.text.strip()
        periodicidade = periodicidade.split('(')[0].strip()  # Ex: "Ano(5):" vira "Ano"
    else:
        st.error("Não foi possível identificar a periodicidade.")
        return pd.DataFrame()

    # Coletar a unidade de medida diretamente dos dados da tabela
    try:
        especificacao = df[df.columns[-1]].unique()[0]
    except KeyError:
        st.error("Erro ao coletar a unidade de medida.")
        return pd.DataFrame()

    # Construção do nome da coluna com os dados corretos
    coluna_valor = f'{nome_tabela} - {especificacao} - {variavel} - {localidade}'
    for char in ':/\\[]':
        coluna_valor = coluna_valor.replace(char, '.')

    # Verificar se existe a coluna de data com base na periodicidade
    coluna_data = f"{periodicidade} (Código)"
    if coluna_data in df.columns:
        # Processamento de datas com base na periodicidade
        if df[coluna_data].astype(str).str.len().max() == 6:
            df['data'] = pd.to_datetime(df[coluna_data], format='%Y%m')
        elif df[coluna_data].astype(str).str.len().max() == 4:
            df['data'] = pd.to_datetime(df[coluna_data], format='%Y')
        else:
            st.error("Formato de data desconhecido.")
            return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
    else:
        st.error(f"Coluna de data '{coluna_data}' não encontrada.")
        return pd.DataFrame()

    # Preparar a série temporal com base nos dados
    timeserie_df = pd.DataFrame({
        'data': df['data'],
        coluna_valor: pd.to_numeric(df['Valor'], errors='coerce')  # Usar o campo correto para valor
    })

    # Remover linhas com valores nulos
    timeserie_df.dropna(inplace=True)

    return timeserie_df

# '---------------------------------------------------------------------------------------------------'

# Função principal
def api_ibge():
    # Carregar dados se ainda não estiverem no estado da sessão
    if 'df_metadados' not in st.session_state:
        carregar_dados()

    # Verifique se 'df_metadados' está no session_state e inicialize se necessário
    if 'df_metadados' not in st.session_state:
        st.session_state['df_metadados'] = pd.DataFrame()

    # Agora você pode acessar 'df_metadados' com segurança
    if not st.session_state['df_metadados'].empty:
        # Seu código para quando o DataFrame não estiver vazio
        st.write("Dados de metadados disponíveis")
    else:
        st.write("Nenhum dado disponível")
    
    # Definir título e cabeçalho da aplicação
    st.title('API de Dados do IBGE')
    st.header('Selecione uma tabela abaixo')
    
    # Criar 'df_ibge_temp' apenas se ele não existir
    if 'df_ibge_temp' not in st.session_state:
        st.session_state['df_ibge_temp'] = pd.DataFrame()

    # Divisão em tabs
    tab1, tab2, tab3 = st.tabs(['Tabela', 'Parâmetros', 'Dados'])
    selecao_metadados = st.session_state['df_metadados'].iloc[selecao_metadados].index.tolist()
    with tab1:
        # Função para criar o dataframe selecionável e aplicar o filtro de códigos da tabela
        selecao_metadados = criar_dataframe_selecionavel(st.session_state['df_metadados'], 'Metadados das Tabelas', 'Selecione as Tabelas', 'df_metadados')
        if selecao_metadados:
            codigos_metadados = st.session_state['df_metadados'].iloc[selecao_metadados].index.tolist()
            codigos_tabelas_selecionados = list(set(codigos_metadados))  # Não precisa usar interseção pois inicializa com os códigos selecionados
        
            col1, col2, col3 = st.columns([4, 1, 1])
            # Exibe o número total e filtrado de registros
            col2.metric(label="Tabelas Filtradas", value=st.session_state['df_metadados_filtrado'])
            aplicar_filtros = col2.button('Aplicar Filtros')
            col3.metric(label="Tabelas Totais", value=st.session_state['df_metadados_total'])
            resetar_filtros = col3.button('Resetar Filtros')
            
            if col1.toggle('Usar filtros avançados'):
                with st.expander('Filtros', expanded=True):
                    col0, col1, col2, col3 = st.columns(4)
                    
                    # Filtro de Status
                    with col0:
                        df_status_unico = st.session_state['df_metadados']['Status'].drop_duplicates().reset_index(drop=True)
                        selecoes_status = criar_dataframe_selecionavel(df_status_unico, 'Status', 'Selecione o(s) Status', 'df_status', col0, hide_index=True)
                        if selecoes_status:
                            valores_selecionados_status = df_status_unico.iloc[selecoes_status].values
                            codigos_tabelas_status = st.session_state['df_metadados'].loc[st.session_state['df_metadados']['Status'].isin(valores_selecionados_status)].index.tolist()
                            codigos_tabelas_selecionados = list(set(codigos_tabelas_selecionados) & set(codigos_tabelas_status))

                    # Filtros de Assunto, Pesquisa e Fonte
                    col_assunto, col_pesquisa, col_fonte = st.columns(3)

                    with col_assunto:
                        df_assunto_unico = st.session_state['df_metadados'][['Assunto']].drop_duplicates().reset_index(drop=True)
                        selecoes_assunto = criar_dataframe_selecionavel(df_assunto_unico, 'Assuntos', 'Selecione o(s) assunto(s).', 'df_assunto', col_assunto, hide_index=True)
                        if selecoes_assunto:
                            valores_selecionados_assunto = df_assunto_unico.iloc[selecoes_assunto]['Assunto'].tolist()
                            codigos_tabelas_assunto = st.session_state['df_metadados'].loc[st.session_state['df_metadados']['Assunto'].isin(valores_selecionados_assunto)].index.tolist()
                            codigos_tabelas_selecionados = list(set(codigos_tabelas_selecionados) & set(codigos_tabelas_assunto))

                    with col_pesquisa:
                        df_pesquisa_unico = st.session_state['df_metadados'][['Pesquisa']].drop_duplicates().reset_index(drop=True)
                        selecoes_pesquisa = criar_dataframe_selecionavel(df_pesquisa_unico, 'Pesquisa', 'Selecione a(s) pesquisa(s).', 'df_pesquisa', col_pesquisa, hide_index=True)
                        if selecoes_pesquisa:
                            valores_selecionados_pesquisa = df_pesquisa_unico.iloc[selecoes_pesquisa]['Pesquisa'].tolist()
                            codigos_tabelas_pesquisa = st.session_state['df_metadados'].loc[st.session_state['df_metadados']['Pesquisa'].isin(valores_selecionados_pesquisa)].index.tolist()
                            codigos_tabelas_selecionados = list(set(codigos_tabelas_selecionados) & set(codigos_tabelas_pesquisa))

                    with col_fonte:
                        df_fonte_unico = st.session_state['df_metadados'][['Fonte']].drop_duplicates().reset_index(drop=True)
                        selecoes_fonte = criar_dataframe_selecionavel(df_fonte_unico, 'Fonte', 'Selecione a(s) fonte(s).', 'df_fonte', col_fonte, hide_index=True)
                        if selecoes_fonte:
                            valores_selecionados_fonte = df_fonte_unico.iloc[selecoes_fonte]['Fonte'].tolist()
                            codigos_tabelas_fonte = st.session_state['df_metadados'].loc[st.session_state['df_metadados']['Fonte'].isin(valores_selecionados_fonte)].index.tolist()
                            codigos_tabelas_selecionados = list(set(codigos_tabelas_selecionados) & set(codigos_tabelas_fonte))

                    # Filtros de Níveis, Periodicidade, e Períodos
                    col_niveis, col_periodicidade, col_periodos = st.columns(3)

                    with col_niveis:
                        df_niveis = st.session_state['df_niveis'][st.session_state['df_niveis']['Código Nível'].isin(st.session_state['rel_tabelaXniveis'][st.session_state['rel_tabelaXniveis']['Código Tabela'].isin(st.session_state['df_metadados'].index)]['Código Nível'])]
                        selecoes_niveis = criar_dataframe_selecionavel(df_niveis, 'Níveis Territoriais', 'Selecione o Nível Territorial', 'df_niveis', col_niveis, hide_index=True)
                        if selecoes_niveis:
                            valores_selecionados_niveis = df_niveis.iloc[selecoes_niveis][df_niveis.columns[0]].tolist()
                            rel_niveis = st.session_state['rel_tabelaXniveis'][st.session_state['rel_tabelaXniveis']['Código Nível'].isin(valores_selecionados_niveis)]
                            codigos_tabelas_niveis = rel_niveis['Código Tabela'].unique()
                            codigos_tabelas_selecionados = list(set(codigos_tabelas_selecionados) & set(codigos_tabelas_niveis))

                    with col_periodicidade:
                        df_periodicidade = st.session_state['df_periodicidade'][st.session_state['df_periodicidade']['Código Periodicidade'].isin(
                            st.session_state['rel_tabelaXperiodicidade'][st.session_state['rel_tabelaXperiodicidade']['Código Tabela'].isin(
                                st.session_state['df_metadados'].index)]['Código Periodicidade'])]
                        selecoes_periodicidade = criar_dataframe_selecionavel(df_periodicidade, 'Periodicidade', 'Selecione a Periodicidade', 'df_periodicidade', col_periodicidade, hide_index=True)
                        if selecoes_periodicidade:
                            valores_selecionados_periodicidade = df_periodicidade.iloc[selecoes_periodicidade][df_periodicidade.columns[0]].tolist()
                            rel_periodicidade = st.session_state['rel_tabelaXperiodicidade'][st.session_state['rel_tabelaXperiodicidade']['Código Periodicidade'].isin(valores_selecionados_periodicidade)]
                            codigos_tabelas_periodicidade = rel_periodicidade['Código Tabela'].unique()
                            codigos_tabelas_selecionados = list(set(codigos_tabelas_selecionados) & set(codigos_tabelas_periodicidade))

                    with col_periodos:
                        df_periodos = st.session_state['df_periodos'][st.session_state['df_periodos']['Código Período'].isin(
                            st.session_state['rel_tabelaXperiodos'][st.session_state['rel_tabelaXperiodos']['Código Tabela'].isin(
                                st.session_state['df_metadados'].index)]['Código Período'])]
                        selecoes_periodos = criar_dataframe_selecionavel(df_periodos, 'Períodos', 'Selecione os Períodos', 'df_periodos', col_periodos, hide_index=True)
                        if selecoes_periodos:
                            valores_selecionados_periodos = df_periodos.iloc[selecoes_periodos][df_periodos.columns[0]].tolist()
                            rel_periodos = st.session_state['rel_tabelaXperiodos'][st.session_state['rel_tabelaXperiodos']['Código Período'].isin(valores_selecionados_periodos)]
                            codigos_tabelas_periodos = rel_periodos['Código Tabela'].unique()
                            codigos_tabelas_selecionados = list(set(codigos_tabelas_selecionados) & set(codigos_tabelas_periodos))

                    # Filtros de Variáveis, Classificações e Subclassificações
                    col_variaveis, col_classificacoes, col_subclassificacoes = st.columns(3)

                    with col_variaveis:
                        df_variaveis = st.session_state['df_variaveis'][st.session_state['df_variaveis']['Código Variável'].isin(
                            st.session_state['rel_tabelaXvariaveis'][st.session_state['rel_tabelaXvariaveis']['Código Tabela'].isin(
                                st.session_state['df_metadados'].index)]['Código Variável'])]
                        selecoes_variaveis = criar_dataframe_selecionavel(df_variaveis, 'Variáveis', 'Selecione as Variáveis', 'df_variaveis', col_variaveis, hide_index=True)
                        if selecoes_variaveis:
                            valores_selecionados_variaveis = df_variaveis.iloc[selecoes_variaveis][df_variaveis.columns[0]].tolist()
                            rel_variaveis = st.session_state['rel_tabelaXvariaveis'][st.session_state['rel_tabelaXvariaveis']['Código Variável'].isin(valores_selecionados_variaveis)]
                            codigos_tabelas_variaveis = rel_variaveis['Código Tabela'].unique()
                            codigos_tabelas_selecionados = list(set(codigos_tabelas_selecionados) & set(codigos_tabelas_variaveis))

                    with col_classificacoes:
                        df_classificacoes = st.session_state['df_classificacoes'][st.session_state['df_classificacoes']['Código Classificação'].isin(
                            st.session_state['rel_tabelaXclassificacoes'][st.session_state['rel_tabelaXclassificacoes']['Código Tabela'].isin(
                                st.session_state['df_metadados'].index)]['Código Classificação'])]
                        selecoes_classificacoes = criar_dataframe_selecionavel(df_classificacoes, 'Classificações', 'Selecione as Classificações', 'df_classificacoes', col_classificacoes, hide_index=True)
                        if selecoes_classificacoes:
                            valores_selecionados_classificacoes = df_classificacoes.iloc[selecoes_classificacoes][df_classificacoes.columns[0]].tolist()
                            rel_classificacoes = st.session_state['rel_tabelaXclassificacoes'][st.session_state['rel_tabelaXclassificacoes']['Código Classificação'].isin(valores_selecionados_classificacoes)]
                            codigos_tabelas_classificacoes = rel_classificacoes['Código Tabela'].unique()
                            codigos_tabelas_selecionados = list(set(codigos_tabelas_selecionados) & set(codigos_tabelas_classificacoes))

                    with col_subclassificacoes:
                        df_subclassificacoes = st.session_state['df_subclassificacoes'][st.session_state['df_subclassificacoes']['Código Subclassificação'].isin(
                            st.session_state['rel_tabelaXsubclassificacoes'][st.session_state['rel_tabelaXsubclassificacoes']['Código Tabela'].isin(
                                st.session_state['df_metadados'].index)]['Código Subclassificação'])]
                        selecoes_subclassificacoes = criar_dataframe_selecionavel(df_subclassificacoes, 'Subclassificações', 'Selecione as Subclassificações', 'df_subclassificacoes', col_subclassificacoes, hide_index=True)
                        if selecoes_subclassificacoes:
                            valores_selecionados_subclassificacoes = df_subclassificacoes.iloc[selecoes_subclassificacoes][df_subclassificacoes.columns[0]].tolist()
                            rel_subclassificacoes = st.session_state['rel_tabelaXsubclassificacoes'][st.session_state['rel_tabelaXsubclassificacoes']['Código Subclassificação'].isin(valores_selecionados_subclassificacoes)]
                            codigos_tabelas_subclassificacoes = rel_subclassificacoes['Código Tabela'].unique()
                            codigos_tabelas_selecionados = list(set(codigos_tabelas_selecionados) & set(codigos_tabelas_subclassificacoes))

            if aplicar_filtros:
                for key in ['df_metadados']:
                    aplicar_filtro_por_codigos_tabelas(key, codigos_tabelas_selecionados)
                    st.json({"Codigos Tabela Selecionados": codigos_tabelas_selecionados})
                    st.rerun()

            # Botão para resetar filtros
            if resetar_filtros:
                carregar_dados()
                st.session_state['dados_ibge_coletados'] = False
                st.session_state['df_ibge_temp'] = pd.DataFrame()
                st.session_state['df_metadados'] = {}
                st.rerun()

            # Mensagem final de seleção da tabela
            if len(codigos_tabelas_selecionados) == 1:
                codigo_tabela = codigos_tabelas_selecionados[0]
                st.write(codigos_tabelas_selecionados)
                st.session_state['codigo_tabela'] = codigo_tabela  # Armazenar o código da tabela no session_state
                st.success(f'Tabela {codigo_tabela} selecionada. Clique na tab "Parâmetros"')
            else:
                st.warning('Por favor, selecione apenas uma tabela.')
                
        with tab2:
            if len(codigos_tabelas_selecionados) == 1:
                codigo_tabela = codigos_tabelas_selecionados[0]
                st.success(f"Tabela {codigo_tabela} selecionada")
                st.title("Especificar parâmetros da série temporal")
                st.write("""
                    Escolha uma variável, um nível territorial, uma localidade, e se aplicável, as classificações e subclassificações disponíveis.
                    Uma série temporal será gerada, composta por data e o campo de valores. A coluna de valores terá como título a descrição 
                    que vem na série temporal (normalmente o último campo), concatenado com a localidade escolhida.
                    As datas serão formatadas no padrão dd/mm/aaaa, representando o último dia de cada período.
                """)

                # Passo 2: Seleção de variáveis da API da tabela e exibição em formato de DataFrame selecionável
                variaveis = obter_variaveis(codigo_tabela)
                df_variaveis = pd.DataFrame(variaveis)  # Convertendo variáveis para DataFrame
                
                # Utilizando a função de DataFrame selecionável
                variavel_selecionada = criar_dataframe_selecionavel(df_variaveis, 'Variáveis', 'Selecione uma variável', 'variaveis')
                
                if variavel_selecionada:
                    variavel_escolhida = df_variaveis.iloc[variavel_selecionada[0]]  # Seleção de uma única variável
                    st.write(f'Variável selecionada: {variavel_escolhida["Nome Variável"]}')

                    # Passo 3: Carregar classificações e subclassificações da API
                    classificacoes = obter_classificacoes_subclassificacoes(codigo_tabela)
                    selecoes_classificacoes = exibir_classificacoes_subclassificacoes(classificacoes)

                    # Seleção de nível territorial e localidade
                    nivel, localidade, df_localidades = selecionar_niveis_localidades(codigo_tabela)

                    if nivel and localidade:
                        
                        st.write(f'Nível territorial selecionado: {nivel}')
                        st.write(f'Localidade selecionada: {localidade}')
                        st.session_state['parametros_ibge'] = {
                            'codigo_tabela': codigo_tabela,
                            'nome_tabela': st.session_state['df_metadados'].loc[codigo_tabela, 'Nome Tabela'],
                            'variavel': df_variaveis.loc[variavel_selecionada, 'Nome Variável'].values[0].split(' - casas decimais')[0],
                            'nivel': nivel,
                            'localidade': df_localidades.loc[localidade, 'Nome'][0],
                            }
                        # Passo 5: Geração do link final e coleta de dados
                        if st.button("Coletar dados"):
                            st.session_state['df_ibge_temp'] = gerar_link_coletar_dados(codigo_tabela, variavel_escolhida, selecoes_classificacoes, nivel, localidade)
                            
                            if not st.session_state['df_ibge_temp'].empty:
                                st.session_state['dados_ibge_coletados'] = True
                                st.success('Dados coletados! Vá para a tab Dados')
                            else:
                                st.session_state['dados_ibge_coletados'] = False
                                st.error('Falha ao coletar os dados.')
                    else:
                        st.warning("Por favor, selecione um nível territorial e uma localidade.")
                else:
                    st.warning("Por favor, selecione uma variável.")
            else:
                st.warning('Por favor, selecione uma tabela na tab "Tabela".')


        with tab3:
            if 'df_ibge_temp' in st.session_state and not st.session_state['df_ibge_temp'].empty:
                st.success('Dados coletados!')
                st.dataframe(st.session_state['df_ibge_temp'], use_container_width=True)

                # Gerar a série temporal se ainda não foi gerada
                if 'ts_ibge_temp' not in st.session_state:
                    st.session_state['ts_ibge_temp'] = gerar_timeserie(
                        st.session_state['df_ibge_temp']
                    )

                # Verificar se a série temporal foi gerada corretamente
                if 'ts_ibge_temp' in st.session_state and not st.session_state['ts_ibge_temp'].empty:
                    ts_ibge_temp = st.session_state['ts_ibge_temp'].copy()

                    # Formatando o campo de data
                    ts_ibge_temp['data'] = ts_ibge_temp['data'].dt.strftime('%d/%m/%Y')
                    ts_ibge_temp.set_index('data', inplace=True)

                    st.subheader("Série Temporal Gerada")
                    st.dataframe(ts_ibge_temp, use_container_width=True)

                    # Adicionar a opção para normalizar os dados
                    normalizar = st.toggle("Normalizar Dados", value=False)
                    if normalizar:
                        valores = (ts_ibge_temp.iloc[:, 0] - ts_ibge_temp.iloc[:, 0].min()) / (ts_ibge_temp.iloc[:, 0].max() - ts_ibge_temp.iloc[:, 0].min())
                    else:
                        valores = ts_ibge_temp.copy()

                    # Exibir gráfico com a série temporal
                    st.line_chart(valores)

                    # Botão para enviar para pré-processamento
                    if st.button("Enviar para Pré-processamento"):
                        if 'df_original' in st.session_state and not st.session_state['df_original'].empty:
                            # Concatena a nova série com as séries existentes
                            st.session_state['df_original'] = pd.concat([st.session_state['df_original'], ts_ibge_temp], axis=1)
                        else:
                            # Se for a primeira série, apenas armazena
                            st.session_state['df_original'] = ts_ibge_temp.copy()

                        st.success("Dados enviados para pré-processamento com sucesso!")
                else:
                    st.error("A série temporal ainda não foi gerada. Verifique os parâmetros.")
            else:
                st.warning('Dados não coletados. Certifique-se de selecionar uma tabela e especificar os parâmetros da consulta.')

if __name__ == '__main__':
    # Configurar layout wide
    st.set_page_config(layout="wide")
    api_ibge()
