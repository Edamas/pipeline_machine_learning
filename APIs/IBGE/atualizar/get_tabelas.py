import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import calendar

MARGEM = 20
inicio = 1  # Definindo o ponto de início corretamente
fim = 10000
batch_size = 10  # Salvamento a cada 10 tabelas processadas

# Dicionários para armazenar valores únicos sem duplicação
variaveis = {}
niveis_geograficos = {}
classificacoes = {}
subclassificacoes = {}
periodicidade = {}
periodos = {}

# Listas para armazenar relacionamentos e metadados
metadados_tabelas = []
rel_tabelas_variaveis = []
rel_tabelas_classificacoes = []
rel_tabelas_subclassificacoes = []
rel_tabelas_niveis = []
rel_tabelas_periodicidade = []
rel_tabelas_periodos = []

# Função para converter o período para o último dia
def converter_periodo(periodo):
    if len(periodo) == 4:  # Exemplo: '2022'
        return f'31/12/{periodo}'
    elif len(periodo) == 6:  # Exemplo: '202212'
        ano = int(periodo[:4])
        mes = int(periodo[4:])
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        return f'{ultimo_dia:02d}/{mes:02d}/{ano}'
    return periodo  # Retorna o período como está, se não for 'aaaa' ou 'aaaamm'

# Função para salvar os dados nos CSVs
def salvar_dados():
    # Definir o caminho de salvamento
    caminho_base = 'C:/_onedrive/OneDrive/Documentos/programacao/streamlit_receber_datasets/APIs/IBGE/'
    
    # Criar DataFrames a partir dos dicionários
    df_variaveis = pd.DataFrame(list(variaveis.values()), columns=['Código Variável', 'Nome Variável']).sort_values(by='Código Variável')
    df_niveis_geograficos = pd.DataFrame(list(niveis_geograficos.values()), columns=['Código Nível', 'Nome Nível']).sort_values(by='Código Nível')
    df_classificacoes = pd.DataFrame(list(classificacoes.values()), columns=['Código Classificação', 'Nome Classificação']).sort_values(by='Código Classificação')
    df_subclassificacoes = pd.DataFrame(list(subclassificacoes.values()), columns=['Código Subclassificação', 'Nome Subclassificação', 'Código Classificação']).sort_values(by='Código Subclassificação')
    df_periodicidade = pd.DataFrame(list(periodicidade.values()), columns=['Código Periodicidade', 'Nome Periodicidade']).sort_values(by='Código Periodicidade')
    df_periodos = pd.DataFrame(list(periodos.values()), columns=['Código Período', 'Nome Período']).sort_values(by='Código Período')

    # Criar DataFrames a partir das listas de relacionamentos
    df_metadados = pd.DataFrame(metadados_tabelas, columns=['Código Tabela', 'Nome Tabela', 'Pesquisa', 'Assunto', 'Status', 'Atualização', 'Notas', 'Fonte']).sort_values(by='Código Tabela')
    df_rel_tabelas_variaveis = pd.DataFrame(rel_tabelas_variaveis, columns=['Código Tabela', 'Código Variável']).sort_values(by='Código Tabela')
    df_rel_tabelas_classificacoes = pd.DataFrame(rel_tabelas_classificacoes, columns=['Código Tabela', 'Código Classificação']).sort_values(by='Código Tabela')
    df_rel_tabelas_subclassificacoes = pd.DataFrame(rel_tabelas_subclassificacoes, columns=['Código Tabela', 'Código Subclassificação']).sort_values(by='Código Tabela')
    df_rel_tabelas_niveis = pd.DataFrame(rel_tabelas_niveis, columns=['Código Tabela', 'Código Nível']).sort_values(by='Código Tabela')
    df_rel_tabelas_periodicidade = pd.DataFrame(rel_tabelas_periodicidade, columns=['Código Tabela', 'Código Periodicidade']).sort_values(by='Código Tabela')
    df_rel_tabelas_periodos = pd.DataFrame(rel_tabelas_periodos, columns=['Código Tabela', 'Código Período']).sort_values(by='Código Tabela')

    # Converter colunas para inteiro, onde aplicável
    df_variaveis['Código Variável'] = df_variaveis['Código Variável'].astype(int)
    df_niveis_geograficos['Código Nível'] = df_niveis_geograficos['Código Nível'].astype(int)
    df_classificacoes['Código Classificação'] = df_classificacoes['Código Classificação'].astype(int)
    df_subclassificacoes['Código Subclassificação'] = df_subclassificacoes['Código Subclassificação'].astype(int)
    df_periodos['Código Período'] = df_periodos['Código Período'].astype(int)

    # Salvar os DataFrames em arquivos CSV
    df_variaveis.to_csv(f'{caminho_base}variaveis.csv', index=False, sep='\t')
    df_niveis_geograficos.to_csv(f'{caminho_base}niveis_geograficos.csv', index=False, sep='\t')
    df_classificacoes.to_csv(f'{caminho_base}classificacoes.csv', index=False, sep='\t')
    df_subclassificacoes.to_csv(f'{caminho_base}subclassificacoes.csv', index=False, sep='\t')
    df_periodicidade.to_csv(f'{caminho_base}periodicidade.csv', index=False, sep='\t')
    df_periodos.to_csv(f'{caminho_base}periodos.csv', index=False, sep='\t')
    df_metadados.to_csv(f'{caminho_base}metadados_tabelas.csv', index=False, sep='\t')
    df_rel_tabelas_variaveis.to_csv(f'{caminho_base}tabela_x_variaveis.csv', index=False, sep='\t')
    df_rel_tabelas_classificacoes.to_csv(f'{caminho_base}tabela_x_classificacoes.csv', index=False, sep='\t')
    df_rel_tabelas_subclassificacoes.to_csv(f'{caminho_base}tabela_x_subclassificacoes.csv', index=False, sep='\t')
    df_rel_tabelas_niveis.to_csv(f'{caminho_base}tabela_x_niveis.csv', index=False, sep='\t')
    df_rel_tabelas_periodicidade.to_csv(f'{caminho_base}tabela_x_periodicidade.csv', index=False, sep='\t')
    df_rel_tabelas_periodos.to_csv(f'{caminho_base}tabela_x_periodos.csv', index=False, sep='\t')


# Função para processar cada tabela e extrair os parâmetros
def processar_tabela(tabela_numero):
    global variaveis, niveis_geograficos, classificacoes, subclassificacoes, periodicidade, periodos
    global metadados_tabelas, rel_tabelas_variaveis, rel_tabelas_classificacoes, rel_tabelas_subclassificacoes, rel_tabelas_niveis, rel_tabelas_periodicidade
    global rel_tabelas_periodos

    print(f"Processando tabela número: {tabela_numero}")  # Log adicional de progresso

    tabela = {}
    erros = []
    link_consulta = f'https://apisidra.ibge.gov.br/desctabapi.aspx?c={tabela_numero}'
    try:
        response = requests.get(link_consulta, timeout=10)  # Adicionando timeout
        if response.status_code == 200:
            content = BeautifulSoup(response.content, 'html.parser')
            try:
                msgerro = content.find('span', id=lambda x: x and x.startswith('lblMensagem')).text
                if msgerro:
                    erros.append(msgerro)
            except Exception as e:
                erros.append(f"Erro ao processar o conteúdo da tabela {tabela_numero}: {e}")
        else:
            erros.append(f"Erro de resposta {response.status_code} para a tabela {tabela_numero}")
    except Exception as e:
        erros.append(f"Erro de conexão ao acessar a tabela {tabela_numero}: {e}")

    if not erros:
        # Capturar nome da tabela, pesquisa, assunto, status, atualização, notas e fonte
        nome_tabela = content.find('span', id=lambda x: x and x.startswith('lblNomeTabela')).text
        pesquisa = content.find('span', id=lambda x: x and x.startswith('lblNomePesquisa')).text
        assunto = content.find('span', id=lambda x: x and x.startswith('lblNomeAssunto')).text
        status = "Ativa" if "série encerrada" not in nome_tabela.lower() else "Série encerrada"
        atualizacao = content.find('span', id=lambda x: x and x.startswith('lblDataAtualizacao')).text
        notas = '; '.join([nota.text for nota in content.find_all('span', {'id': 'lblTextoDescricao'})])
        fonte = '; '.join([fonte.text for fonte in content.find_all('span', {'id': 'lblFonte'})])

        # Atualizar tabela de metadados
        metadados_tabelas.append([tabela_numero, nome_tabela, pesquisa, assunto, status, atualizacao, notas, fonte])

        # Capturar variáveis
        variaveis_list = content.find_all('tr')
        for var in variaveis_list:
            var_codigo = var.find('span', id=lambda x: x and x.startswith('lstVariaveis_lblIdVariavel')).text if var.find('span', id=lambda x: x and x.startswith('lstVariaveis_lblIdVariavel')) else None
            var_nome = var.find('span', id=lambda x: x and x.startswith('lstVariaveis_lblNomeVariavel')).text if var.find('span', id=lambda x: x and x.startswith('lstVariaveis_lblNomeVariavel')) else None
            if var_codigo and var_nome:
                var_codigo = int(var_codigo)  # Convertendo o código para inteiro
                if var_codigo not in variaveis:
                    variaveis[var_codigo] = [var_codigo, var_nome]
                rel_tabelas_variaveis.append([tabela_numero, var_codigo])

        # Capturar classificações e subclassificações
        classificacoes_list = content.find_all('span', id=lambda x: x and x.startswith('lstClassificacoes_lblIdClassificacao'))
        for classificacao in classificacoes_list:
            classificacao_codigo = classificacao.text
            classificacao_nome = classificacao.find_next('span', {'class': 'tituloLinha'}).text if classificacao.find_next('span', {'class': 'tituloLinha'}) else None
            if classificacao_codigo and classificacao_nome:
                classificacao_codigo = int(classificacao_codigo)  # Convertendo o código para inteiro
                if classificacao_codigo not in classificacoes:
                    classificacoes[classificacao_codigo] = [classificacao_codigo, classificacao_nome]
                rel_tabelas_classificacoes.append([tabela_numero, classificacao_codigo])

                # Capturar subclassificações
                subitens = classificacao.find_next('table').find_all('tr')
                for subitem in subitens:
                    subitem_codigo = subitem.find('span', style='color:Red').text if subitem.find('span', style='color:Red') else None
                    subitem_nome = subitem.find_next('span', id=lambda x: x and 'lblNomeCategoria' in x).text if subitem.find_next('span', id=lambda x: x and 'lblNomeCategoria' in x) else None
                    if subitem_codigo and subitem_nome:
                        subitem_codigo = int(subitem_codigo)  # Convertendo o código da subclassificação para inteiro
                        if subitem_codigo not in subclassificacoes:
                            subclassificacoes[subitem_codigo] = [subitem_codigo, subitem_nome, classificacao_codigo]
                        rel_tabelas_subclassificacoes.append([tabela_numero, subitem_codigo])

        # Capturar níveis territoriais
        niveis_territoriais = content.find_all('span', id=lambda x: x and x.startswith('lstNiveisTerritoriais_lblNomeNivelterritorial'))
        for i, nivel_nome in enumerate(niveis_territoriais):
            nivel_codigo = content.find('span', id=f'lstNiveisTerritoriais_lblIdNivelterritorial_{i}').text
            if nivel_codigo and nivel_nome:
                nivel_codigo = int(nivel_codigo)  # Convertendo o código para inteiro
                if nivel_codigo not in niveis_geograficos:
                    niveis_geograficos[nivel_codigo] = [nivel_codigo, nivel_nome.text]
                rel_tabelas_niveis.append([tabela_numero, nivel_codigo])

        # Capturar periodicidade
        periodicidade_element = content.find('span', id='lblNomePeriodo')
        if periodicidade_element:
            periodicidade_valor = periodicidade_element.text.split('(')[0].strip()  # Mantém como string
            if periodicidade_valor not in periodicidade:
                periodicidade[periodicidade_valor] = [periodicidade_valor, periodicidade_valor]
            rel_tabelas_periodicidade.append([tabela_numero, periodicidade_valor])

        # Capturar períodos
        periodos_element = content.find('span', id='lblPeriodoDisponibilidade')
        if periodos_element:
            periodos_list = periodos_element.text.split(", ")
            for periodo in periodos_list:
                if len(periodo) == 6:  # Formato aaaamm
                    periodo_codigo = int(periodo[:6])  # Código como inteiro (aaaamm)
                else:  # Formato aaaa
                    periodo_codigo = int(periodo[:4])  # Código como inteiro (aaaa)
                periodo_nome = converter_periodo(periodo)  # Converte para o último dia do período
                if periodo_codigo not in periodos:
                    periodos[periodo_codigo] = [periodo_codigo, periodo_nome]
                rel_tabelas_periodos.append([tabela_numero, periodo_codigo])

    else:
        print(f"Erro(s) ao processar a tabela {tabela_numero}: {', '.join(erros)}")

# Loop para processar as tabelas e salvar periodicamente
for tabela_numero in range(inicio, fim + 1):
    processar_tabela(tabela_numero)
    
    # Salvar a cada 10 tabelas
    if tabela_numero % 10 == 0:
        salvar_dados()
        print('.', end='')

# Salvar o restante após o loop
salvar_dados()
print("Processo concluído!")
