# api_ibge.py
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from manager import series_manager


#@st.cache_data
def cache_coletar_dados(url):
    return coletar_dados(url)


# A seleção é então retornada como uma lista de índices selecionados.
def criar_dataframe_selecionavel(df, titulo, descricao, df_key, hide_index=False):
    st.write(f"**{titulo}**: {descricao}")
    event = st.dataframe(df, use_container_width=True, hide_index=hide_index, on_select="rerun", selection_mode="single-row")

    # Armazena o número de registros filtrados
    st.session_state[f'{df_key}_filtrado'] = len(df)
    if event and 'selection' in event:
        if 'rows' in event['selection']:
            if event['selection']['rows']:
                return df.iloc[event['selection']['rows']].index.tolist()
    return []


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
    url_consulta = f"https://apisidra.ibge.gov.br/desctabapi.aspx?c={codigo_tabela}"
    with st.spinner(f'Consultando parâmetros da tabela `{codigo_tabela}`'):
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
        return df_dados

    else:
        st.error(f"Coluna de período '{nome_periodo}' não encontrada no DataFrame.")
        return pd.DataFrame()

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
        
        nome_coluna_valor = f'{variavel} {unidade} {classificacoes} {localidade}'
        
        # Prepara a série temporal
        timeserie_df = pd.DataFrame({
            'data': df['data'],
            nome_coluna_valor: pd.to_numeric(df['Valor'], errors='coerce')  # Usar o campo correto para valor
        })
        timeserie_df.set_index('data', inplace=True)
        
        return timeserie_df


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


# Função para extrair texto de forma segura
def extrair_texto(element, valor_default="Desconhecido"):
    return element.get_text().strip() if element else valor_default


def get_variaveis_classificacoes(codigo_tabela):
    # URL da API
    url = f"https://apisidra.ibge.gov.br/desctabapi.aspx?c={codigo_tabela}"
    response = requests.get(url)
    response.raise_for_status()
    
    # Parse do conteúdo HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Inicializar dicionários de variáveis e classificações
    variaveis = {}
    classificacoes = {}

    # Coletar as variáveis
    variaveis_elements = soup.find_all('span', id=lambda x: x and x.startswith('lstVariaveis_lblIdVariavel'))
    for variavel in variaveis_elements:
        codigo_variavel = variavel.text.strip()
        nome_variavel = variavel.find_next('span').text.strip()
        variaveis[codigo_variavel] = nome_variavel

    if 'Variavel_ibge_selecionada' not in st.session_state:
        st.session_state['Variavel_ibge_selecionada'] = None
    else:
        variavel_selecionada = st.session_state['Variavel_ibge_selecionada']
    if not st.session_state['Variavel_ibge_selecionada']:
        if f'variaveis_{codigo_tabela}' in st.session_state:
            del st.session_state[f'variaveis_{codigo_tabela}']
            
        # Converter variáveis em DataFrame e apresentar ao usuário
        df_variaveis = pd.DataFrame(list(variaveis.items()), columns=['Código', 'Nome'])

        df_variaveis.set_index('Código', inplace=True)
        variavel_selecionada_indices = criar_dataframe_selecionavel(
            df=df_variaveis, 
            titulo=f'Variáveis para `{nome_variavel}`',
            descricao='Selecione a Variável', 
            df_key=f'variaveis_{codigo_tabela}',  # Chave única para evitar conflitos
            hide_index=False)
        if variavel_selecionada_indices:
            variavel_selecionada_indice = variavel_selecionada_indices[0]
            variavel_selecionada = df_variaveis.loc[variavel_selecionada_indices].index.tolist()[0] if variavel_selecionada_indice else None
            st.session_state['Variavel_ibge_selecionada'] = variavel_selecionada
    else:
        variavel_selecionada = st.session_state['Variavel_ibge_selecionada']

    # Coletar as classificações e subclassificações
    elementos_classificacao = soup.find_all("span", id=lambda value: value and value.startswith("lstClassificacoes_lblClassificacao"))
    classificacoes_selecionadas = []
    for idx, classificacao in enumerate(elementos_classificacao):
        codigo_classificacao = soup.find(id=f'lstClassificacoes_lblIdClassificacao_{idx}').text.strip()
        nome_classificacao = classificacao.text.strip()
        numero_itens_str = soup.find(id=f'lstClassificacoes_lblQuantidadeCategorias_{idx}').text.strip('():')
        numero_itens = int(numero_itens_str) if numero_itens_str.strip().isdigit() else 0
        
        itens = []
        elementos_itens = soup.find_all("span", id=lambda value: value and value.startswith(f'lstClassificacoes_lstCategorias_{idx}_lblIdCategoria_'))
        for item_idx, item in enumerate(elementos_itens):
            codigo_item = item.text.strip()
            nome_item = soup.find(id=f'lstClassificacoes_lstCategorias_{idx}_lblNomeCategoria_{item_idx}').text.strip()
            itens.append({'Código': codigo_item, 'Nome': nome_item})
        
        classificacoes[codigo_classificacao] = {
            "nome": nome_classificacao,
            "número de itens": numero_itens,
            "itens": itens
        }
        
        # Converter classificação em DataFrame e apresentar ao usuário
        df_classificacao = pd.DataFrame(itens)
        if not df_classificacao.empty:
            classificacao_selecionada_indices = criar_dataframe_selecionavel(
                df=df_classificacao, 
                titulo=nome_classificacao, 
                descricao=f'Selecione a classificação para {nome_classificacao}', 
                df_key=f'classificacao_{codigo_classificacao}_{codigo_tabela}_{idx}',  # Chave única para evitar conflitos
                hide_index=False)
            if classificacao_selecionada_indices:
                for indice in classificacao_selecionada_indices:
                    codigo_subclassificacao = df_classificacao.iloc[indice]['Código']
                    classificacoes_selecionadas.append((codigo_classificacao, codigo_subclassificacao))    # Retornar os resultados
    return variavel_selecionada, classificacoes_selecionadas



def contas_nacionais_pib():
    st.title('Fonte de Dados: IBGE')
    st.header('Contas Nacionais e PIB')
    df_metadados = pd.read_excel('inputs/metadados/metadados_ibge.xlsx', sheet_name='Contas Nacionais e PIB')
    df_metadados.set_index('Código Tabela', inplace=True)
    process(df_metadados)

def process(df_metadados):
    st.session_state['Variavel_ibge_selecionada'] = None
    st.session_state['df_metadados'] = df_metadados.copy()
    
    selecao_metadados = criar_dataframe_selecionavel(st.session_state['df_metadados'], 'Metadados das Tabelas', 'Selecione as Tabelas', 'df_metadados', hide_index=False)
    
    if selecao_metadados:
        st.session_state['sel_cod_tab'] = selecao_metadados
        if len(st.session_state['sel_cod_tab']) == 1:
            codigo_tabela = st.session_state['sel_cod_tab'][0]
            st.session_state['codigo_tabela'] = codigo_tabela
            
            variavel, classificacoes = get_variaveis_classificacoes(codigo_tabela)
            
            if classificacoes:
                nao_ha_classificacoes = False
            else:
                nao_ha_classificacoes = True
            st.session_state['parametros_ibge'] = {
                    'codigo_tabela': codigo_tabela,
                    'variavel': variavel,
                    'classificacoes': classificacoes,
                    'nivel': 'N1',
                    'localidade': 1
                }
            
            if not all([
                st.session_state['parametros_ibge']['codigo_tabela'], 
                st.session_state['parametros_ibge']['variavel'],
                st.session_state['parametros_ibge']['classificacoes'] or nao_ha_classificacoes,
                st.session_state['parametros_ibge']['nivel'],
                st.session_state['parametros_ibge']['localidade'],
            ]):
                st.warning('É necessário escolher todos os parâmetros de consulta')
            else:
                # Coleta de dados e envio para análise
                url = gerar_link()
                st.session_state['df_ibge'] = cache_coletar_dados(url)
                if not st.session_state['df_ibge'].empty:
                    st.session_state['df_ibge']['Valor'] = pd.to_numeric(st.session_state['df_ibge']['Valor'], errors='coerce')
                    st.session_state['df_ibge'].dropna(subset=['Valor'], inplace=True)
                    registros_validos = st.session_state['df_ibge']['Valor'].count()
                    if registros_validos == 0:
                        st.error('Nenhum dado numérico retornado para a série selecionada.')
                    else:
                        ts = gerar_timeserie()
                        ts.columns = [col.replace('Brasil - Brasil', 'Brasil') for col in ts.columns]
                        
                        # Integrar a série com df_main
                        if 'df_main' in st.session_state and not st.session_state['df_main'].empty:
                            st.session_state['df_original'] = st.session_state['df_main'].combine_first(ts)
                        else:
                            st.session_state['df_main'] = ts.copy()
                            st.session_state['df_original'] = ts.copy()

                        st.session_state['df_editado'] = st.session_state['df_original'].copy()
        else:
            st.warning('Por favor, selecione apenas uma tabela.')
    else:
        st.session_state['sel_cod_tab'] = []

    # Chamar o series_manager()
    series_manager()  


if __name__ == '__main__':
    st.set_page_config(layout="wide")