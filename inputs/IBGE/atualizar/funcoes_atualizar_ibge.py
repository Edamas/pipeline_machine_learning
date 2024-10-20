import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time

# Dicionário atualizado com o número total de localidades por nível, se possui cobertura nacional e o nome de cada nível
localidades_totais_por_nivel = {
    "N1": {"total": 1, "cobertura_nacional": True, "nome": "Brasil"},
    "N2": {"total": 5, "cobertura_nacional": True, "nome": "Grande Região"},
    "N3": {"total": 27, "cobertura_nacional": True, "nome": "Unidade da Federação"},
    "N6": {"total": 5565, "cobertura_nacional": True, "nome": "Município"},
    "N7": {"total": 77, "cobertura_nacional": False, "nome": "Região Metropolitana"},
    "N8": {"total": 137, "cobertura_nacional": True, "nome": "Mesorregião Geográfica"},
    "N9": {"total": 558, "cobertura_nacional": True, "nome": "Microrregião Geográfica"},
    "N10": {"total": 10670, "cobertura_nacional": True, "nome": "Distrito"},
    "N11": {"total": 643, "cobertura_nacional": True, "nome": "Subdistrito"},
    "N13": {"total": 77, "cobertura_nacional": False, "nome": "Região Metropolitana e Subdivisão"},
    "N14": {"total": 5, "cobertura_nacional": False, "nome": "Região Integrada de Desenvolvimento"},
    "N15": {"total": 5, "cobertura_nacional": False, "nome": "Aglomeração Urbana"},
    "N17": {"total": 1000, "cobertura_nacional": False, "nome": "Aglomerado Subnormal"},
    "N18": {"total": 1000, "cobertura_nacional": None, "nome": "Área de Ponderação"},
    "N20": {"total": 1000, "cobertura_nacional": False, "nome": "Área de Divulgação da Amostra para Aglomerados Subnormais"},
    "N21": {"total": 5, "cobertura_nacional": False, "nome": "Total dos municípios das capitais da Grande Região"},
    "N22": {"total": 27, "cobertura_nacional": False, "nome": "Total dos municípios das capitais"},
    "N23": {"total": 1000, "cobertura_nacional": False, "nome": "Arranjo Populacional"},
    "N24": {"total": 133, "cobertura_nacional": True, "nome": "Região Geográfica Intermediária"},
    "N25": {"total": 1000, "cobertura_nacional": False, "nome": "Região Geográfica Imediata"},
    "N29": {"total": 1000, "cobertura_nacional": False, "nome": "Território de Identidade"},
    "N33": {"total": 1000, "cobertura_nacional": False, "nome": "Concentração Urbana"},
    "N70": {"total": 1000, "cobertura_nacional": False, "nome": "Recortes Metropolitanos"},
    "N71": {"total": 1000, "cobertura_nacional": False, "nome": "Categoria Metropolitana"},
    "N72": {"total": 1000, "cobertura_nacional": False, "nome": "Subcategoria Metropolitana"},
    "N101": {"total": 1000, "cobertura_nacional": False, "nome": "País do Mercosul, Bolívia e Chile"},
    "N102": {"total": 1000, "cobertura_nacional": False, "nome": "Bairro"},
    "N103": {"total": 1000, "cobertura_nacional": False, "nome": "Total das áreas - POF"},
    "N110": {"total": 1000, "cobertura_nacional": False, "nome": "Total das áreas - PME"},
    "N111": {"total": 1000, "cobertura_nacional": False, "nome": "Unidade Federativa do Mercosul, Bolívia e Chile"},
    "N121": {"total": 1000, "cobertura_nacional": False, "nome": "Região Hidrográfica"},
    "N122": {"total": 1000, "cobertura_nacional": False, "nome": "Grandes Regiões - PIMES"},
    "N123": {"total": 1000, "cobertura_nacional": False, "nome": "Bioma"},
    "N124": {"total": 1000, "cobertura_nacional": False, "nome": "Corpo d'água"},
    "N125": {"total": 1000, "cobertura_nacional": False, "nome": "Terra Indígena por Unidade da Federação"},
    "N127": {"total": 1000, "cobertura_nacional": False, "nome": "Núcleo de desertificação"},
    "N128": {"total": 1000, "cobertura_nacional": False, "nome": "Praia"},
    "N129": {"total": 1000, "cobertura_nacional": False, "nome": "Território da Cidadania"},
    "N130": {"total": 1000, "cobertura_nacional": False, "nome": "Capital/não capital de Unidade da Federação"},
    "N131": {"total": 1000, "cobertura_nacional": False, "nome": "Amazônia Legal"},
    "N132": {"total": 1000, "cobertura_nacional": False, "nome": "Semiárido"},
    "N133": {"total": 1000, "cobertura_nacional": False, "nome": "Semiárido de Unidade da Federação"},
    "N134": {"total": 1000, "cobertura_nacional": False, "nome": "Amazônia Legal de Unidade da Federação"},
    "N145": {"total": 1000, "cobertura_nacional": False, "nome": "Território Quilombola por Unidade da Federação"},
    "N151": {"total": 1000, "cobertura_nacional": False, "nome": "Categoria da Aglomeração Urbana"},
    "N1011": {"total": 1000, "cobertura_nacional": False, "nome": "Municípios Costeiros"},
    "N1013": {"total": 1000, "cobertura_nacional": False, "nome": "Municípios de Faixa de Fronteira"},
    "N1100": {"total": 1000, "cobertura_nacional": False, "nome": "Brasil, sem especificação de Unidade da Federação"},
    "N1101": {"total": 1000, "cobertura_nacional": False, "nome": "Ignorado"},
    "N1102": {"total": 1000, "cobertura_nacional": False, "nome": "Estrangeiro"},
    "N1103": {"total": 1, "cobertura_nacional": True, "nome": "Total"},
    "N1104": {"total": 1000, "cobertura_nacional": False, "nome": "Unidade da Federação, sem especificação de Município"},
    "N1105": {"total": 1000, "cobertura_nacional": False, "nome": "Área de influência - PNSB"},
    "N1124": {"total": 1000, "cobertura_nacional": False, "nome": "Coordenação Regional da Funai"},
    "N1125": {"total": 1000, "cobertura_nacional": False, "nome": "Terra Indígena"},
    "N1145": {"total": 1000, "cobertura_nacional": False, "nome": "Território Quilombola"}
}

# Função para processar as classificações e subclassificações
def processar_classificacoes(soup):
    """
    Processa e extrai as classificações e suas respectivas subclassificações da tabela.

    Parâmetros:
        soup (BeautifulSoup): Objeto BeautifulSoup da página HTML da tabela.

    Retorna:
        dict: Dicionário contendo as classificações e suas subclassificações.
    """
    classificacoes = {}
    elementos_classificacao = soup.find_all("span", id=lambda value: value and value.startswith("lstClassificacoes_lblClassificacao_"))
    
    for idx, classificacao in enumerate(elementos_classificacao):
        codigo_classificacao = extrair_texto(soup.find(id=f'lstClassificacoes_lblIdClassificacao_{idx}'))
        nome_classificacao = extrair_texto(classificacao)
        numero_itens_str = extrair_texto(soup.find(id=f'lstClassificacoes_lblQuantidadeCategorias_{idx}')).strip('():')
        numero_itens = int(numero_itens_str) if numero_itens_str.strip().isdigit() else 0
        
        itens = {}
        elementos_itens = soup.find_all("span", id=lambda value: value and value.startswith(f'lstClassificacoes_lstCategorias_{idx}_lblIdCategoria_'))
        
        for item_idx, item in enumerate(elementos_itens):
            codigo_item = extrair_texto(item)
            nome_item = extrair_texto(soup.find(id=f'lstClassificacoes_lstCategorias_{idx}_lblNomeCategoria_{item_idx}'))
            itens[codigo_item] = nome_item
        
        classificacoes[codigo_classificacao] = {
            "nome": nome_classificacao,
            "número de itens": numero_itens,
            "itens": itens
        }
    
    if not classificacoes:
        classificacoes = {}
    
    return classificacoes




def converter_periodo(periodo):
    """
    Converte o período fornecido no formato 'aaaa' ou 'aaaamm' para o último dia do ano ou mês correspondente.

    Parâmetros:
        periodo (str): Período no formato 'aaaa' ou 'aaaamm'.

    Retorna:
        str: Data convertida no formato 'dd/mm/aaaa'.
    """
    if len(periodo) == 4:  # Formato 'aaaa'
        return f"31/12/{periodo}"
    elif len(periodo) == 6:  # Formato 'aaaamm'
        ano = int(periodo[:4])
        mes = int(periodo[4:])
        if mes == 12:
            ultimo_dia = 31
        else:
            ultimo_dia = (datetime(ano, mes + 1, 1) - timedelta(days=1)).day
        return f"{ultimo_dia:02d}/{mes:02d}/{ano}"
    else:
        return "Período inválido"

# Função para processar os períodos
def processar_periodos(soup):
    """
    Processa e extrai os períodos da tabela.

    Parâmetros:
        soup (BeautifulSoup): Objeto BeautifulSoup da página HTML da tabela.

    Retorna:
        dict: Dicionário contendo os períodos extraídos e informações adicionais.
    """
    periodos = {}
    elemento_periodo = soup.find("span", id=lambda value: value and value.startswith("lblNomePeriodo"))
    periodicidade_info = elemento_periodo.text
    periodicidade_nome, num_periodos = periodicidade_info.split('(')
    periodicidade_nome = periodicidade_nome.strip()
    num_periodos = int(num_periodos.strip('):'))
    
    valores_periodo = soup.find("span", id=f"lblPeriodoDisponibilidade").get_text().split(', ')
    for valor in valores_periodo:
        periodo_original = int(valor.strip())  # Convertendo para número inteiro
        periodo_convertido = converter_periodo(valor.strip())
        periodos[periodo_original] = periodo_convertido

    datas_convertidas = [datetime.strptime(data, "%d/%m/%Y") for data in periodos.values()]
    data_minima = min(datas_convertidas).strftime("%d/%m/%Y") if datas_convertidas else "Desconhecido"
    data_maxima = max(datas_convertidas).strftime("%d/%m/%Y") if datas_convertidas else "Desconhecido"
    numero_registros = len(datas_convertidas)
    frequencia_media = (max(datas_convertidas) - min(datas_convertidas)).days / (numero_registros - 1) if numero_registros > 1 else 0
    dias_sem_registro = (datetime.now() - max(datas_convertidas)).days if datas_convertidas else "Desconhecido"
    intervalo_coberto = (max(datas_convertidas) - min(datas_convertidas)).days if datas_convertidas else "Desconhecido"

    return {
        "Lista de Períodos": {int(key): value for key, value in periodos.items()},
        "Periodicidade": periodicidade_nome,
        "Número de Períodos": num_periodos,
        "Data Mínima": data_minima,
        "Data Máxima": data_maxima,
        "Intervalo Coberto (dias)": intervalo_coberto,
        "Número de Registros": numero_registros,
        "Frequência Média (dias)": frequencia_media,
        "Dias sem Registros até Hoje": dias_sem_registro
    }

def processar_variaveis(soup):
    """
    Processa e extrai as variáveis da tabela.

    Parâmetros:
        soup (BeautifulSoup): Objeto BeautifulSoup da página HTML da tabela.

    Retorna:
        dict: Dicionário contendo as variáveis extraídas.
    """
    variaveis = {}
    variaveis_elements = soup.find_all('span', id=lambda x: x and x.startswith('lstVariaveis_lblIdVariavel'))

    for variavel in variaveis_elements:
        codigo_variavel = variavel.text
        nome_variavel = variavel.find_next('span').text
        variaveis[codigo_variavel] = nome_variavel
            

    return variaveis



def calcular_cobertura(localidades_presentes, localidades_maximas):
    return f"{(localidades_presentes / localidades_maximas) * 100:.2f}" if localidades_maximas > 0 else "0.00"

# Função para extrair texto de forma segura
def extrair_texto(element, valor_default="Desconhecido"):
    return element.get_text().strip() if element else valor_default

# Função para processar os metadados
def processar_metadados(soup, cod_tabela):
    """
    Processa e extrai os metadados da tabela.

    Parâmetros:
        soup (BeautifulSoup): Objeto BeautifulSoup da página HTML da tabela.
        cod_tabela (int): Código da tabela sendo processada.

    Retorna:
        dict: Dicionário contendo os metadados extraídos.
    """
    metadados = {
        "Número": cod_tabela,
        "Nome": extrair_texto(soup.find(id="lblNomeTabela")),
        "Pesquisa": extrair_texto(soup.find(id="lblNomePesquisa")),
        "Assunto": extrair_texto(soup.find(id="lblNomeAssunto")),
        "Última atualização": pd.to_datetime(
            extrair_texto(soup.find(id="lblDataAtualizacao"), None),
            format='%Y-%m-%d %H:%M:%S', errors='coerce'
        ).strftime('%d/%m/%Y %H:%M:%S') if soup.find(id="lblDataAtualizacao") else "Desconhecido",
        "Última Consulta": pd.to_datetime('today').strftime('%d/%m/%Y'),
        "Link de Consulta": f"https://apisidra.ibge.gov.br/desctabapi.aspx?c={cod_tabela}",
        "Nota": extrair_texto(soup.find(id="lblTextoDescricao"), ""),
        "Fonte": extrair_texto(soup.find(id="lblFonte")),
        "Encerrada": any(termo in extrair_texto(soup.find(id="lblNomeTabela")).lower() for termo in ["serie encerrada", "série encerrada", "serie encerada", "série encerrada"]),
        "Número de Variáveis": int(re.search(r'\((\d+)\)', extrair_texto(soup.find("span", id="lblVariaveis"))).group(1))
        if re.search(r'\((\d+)\)', extrair_texto(soup.find("span", id="lblVariaveis"))) else 0
    }
    '''try:
        metadados["Status"] = "Ativa" if (pd.to_datetime('today') - pd.to_datetime(
            extrair_texto(soup.find(id="lblDataAtualizacao"), None),
            format='%Y-%m-%d %H:%M:%S', errors='coerce')).days < 365 else "Inativa"
    except:
        st.write(cod_tabela)
        st.write()'''
    return metadados

def processar_niveis_territoriais(soup, cod_tabela):
    """
    Processa e extrai os níveis territoriais da tabela.

    Parâmetros:
        soup (BeautifulSoup): Objeto BeautifulSoup da página HTML da tabela.
        cod_tabela (int): Código da tabela sendo processada.

    Retorna:
        dict: Dicionário contendo os níveis territoriais extraídos.
    """
    niveis_territoriais = {}
    niveis = soup.find_all("tr")  # Encontra todas as linhas de nível territorial no HTML
    
    for nivel in niveis:
        # Identifica o ID do nível territorial
        nivel_id_span = nivel.find("span", id=lambda value: value and value.startswith("lstNiveisTerritoriais_lblIdNivelterritorial"))
        if nivel_id_span:
            nivel_id = extrair_texto(nivel_id_span).strip()  # Extrai e limpa o texto do ID do nível

            # Nome do nível territorial (Ex: Brasil, Unidade da Federação)
            nome_nivel = extrair_texto(nivel.find("span", id=lambda value: value and value.startswith("lstNiveisTerritoriais_lblNomeNivelterritorial"))).strip()
            
            # Coleta o número de localidades entre parênteses (Ex: "(27)")
            num_localidades_match = re.search(r'\((\d+)\)', extrair_texto(nivel.find("span", id=lambda value: value and value.startswith("lstNiveisTerritoriais_lblQuantidadeUnidadesTerritoriais"))))
            num_localidades = int(num_localidades_match.group(1)) if num_localidades_match else 0
            
            # Gera o link para a lista de localidades, se aplicável
            link_localidades = f"https://apisidra.ibge.gov.br/LisUnitTabAPI.aspx?c={cod_tabela}&n={nivel_id}&i=P"

            # Obtém as localidades através do link gerado
            localidades = obter_localidades(link_localidades)

            # Informações sobre a cobertura nacional e o total de localidades esperadas para o nível
            nivel_info = localidades_totais_por_nivel.get(f"N{nivel_id}", {"total": 1000, "cobertura_nacional": False})
            cobertura_nacional = nivel_info["cobertura_nacional"]
            
            # Calcula a cobertura percentual (localidades presentes / total de localidades)
            cobertura_percentual = calcular_cobertura(
                localidades_presentes=num_localidades,
                localidades_maximas=nivel_info["total"]
            )

            # Armazena as informações extraídas no dicionário
            niveis_territoriais[f"N{nivel_id}"] = {
                "Nome": nome_nivel,
                "Número de Localidades": num_localidades,
                "Localidades Presentes": localidades,
                "Cobertura Nacional": cobertura_nacional,
                "Cobertura (%)": cobertura_percentual,
                "Link para Localidades": link_localidades
            }

    if not niveis_territoriais:
        niveis_territoriais = {
            "NDesconhecido": {
                "Nome": "Desconhecido",
                "Número de Localidades": 0,
                "Localidades Presentes": {0: "Desconhecido"},
                "Cobertura Nacional": False,
                "Cobertura (%)": "0.00",
                "Link para Localidades": f"https://apisidra.ibge.gov.br/LisUnitTabAPI.aspx?c={cod_tabela}&n=Desconhecido&i=P"
            }
        }
    return niveis_territoriais


def obter_localidades(link_localidades):
    """
    Acessa o link das localidades e captura a tabela de localidades presentes.

    Parâmetros:
        link_localidades (str): URL para acessar as localidades.

    Retorna:
        dict: Dicionário contendo as localidades presentes com informações de todas as colunas disponíveis.
    """
    try:
        response = requests.get(link_localidades)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            localidades = {}
            tabela_localidades = soup.find("table", id="grdUnidadeTerritorial")
            if tabela_localidades:
                linhas = tabela_localidades.find_all("tr")[1:]  # Ignorar o cabeçalho
                cabecalhos = [th.get_text(strip=True) for th in tabela_localidades.find_all("th")]
                for idx, linha in enumerate(linhas):
                    colunas = linha.find_all("td")
                    if len(colunas) == len(cabecalhos):
                        localidade_info = {cabecalhos[i]: colunas[i].get_text(strip=True) for i in range(len(colunas))}
                        localidades[idx] = localidade_info
            return localidades if localidades else {0: "Nenhuma localidade encontrada"}
        else:
            return {0: "Erro ao acessar o link. Código de status: " + str(response.status_code)}
    except Exception as e:
        return {0: f"Erro ao acessar localidades: {str(e)}"}

def calcular_cobertura(localidades_presentes, localidades_maximas):
    """
    Calcula a cobertura percentual de localidades presentes em relação ao total.

    Parâmetros:
        localidades_presentes (int): Número de localidades presentes.
        localidades_maximas (int): Número total de localidades possíveis.

    Retorna:
        str: Cobertura percentual formatada.
    """
    if localidades_maximas > 0:
        cobertura = (localidades_presentes / localidades_maximas) * 100
        return f"{cobertura:.2f}"
    return "0.00"


# Função para conectar e obter o BeautifulSoup da página
def conectar(link, max_retries=5, timeout=2):
    """
    Faz a conexão com o link fornecido e retorna o objeto BeautifulSoup da página.

    Parâmetros:
        link (str): URL para acessar.
        max_retries (int): Número máximo de tentativas de reconexão em caso de falha.
        timeout (int): Tempo máximo de espera (em segundos) para estabelecer a conexão.

    Retorna:
        BeautifulSoup: Objeto BeautifulSoup da página HTML acessada, ou None em caso de falha.
    """
    attempt = 1
    while attempt < max_retries:
        try:
            # Faz a requisição com timeout
            response = requests.get(link, timeout=timeout * attempt)
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200:
                return BeautifulSoup(response.content, "html.parser")
            else:
                print(f"Erro HTTP {response.status_code} ao acessar {link}")
                return None
        except requests.exceptions.Timeout:
            print(f"Timeout na tentativa {attempt + 1} ao acessar {link}. Tentando novamente em {attempt} segundos com timeout de {attempt * timeout} segundos")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {link}: {e}")
        

        # Incrementa o número de tentativas
        attempt += 1
        time.sleep(attempt)  # O tempo de espera aumenta conforme o número da tentativa (0, 1, 2, 3, 4)

    print(f"Máximo de tentativas ({max_retries}) excedido para {link}")
    return None