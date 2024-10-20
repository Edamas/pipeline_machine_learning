import streamlit as st
from funcoes_atualizar_ibge import *
import json
import os


# Função para verificar se a tabela deve ser descartada ou aprovada
def aprovar_ou_reprovar(soup):
    # 1. Verificar se o soup não trouxe dados
    if not soup:
        return False, "Soup não trouxe dados", ''
    
    # 2. Verificar se a tabela é inválida
    mensagem_erro = soup.find("span", id="lblMensagem", class_="mensagemErro")  # o código HTML da página 74 não apresenta lblMensagem, portanto, não há mensagem de erro
    if mensagem_erro and len(mensagem_erro.get_text().strip()) > 1:
        return False, f"{mensagem_erro.get_text()}", ''

    # 3. Verificar se a tabela está encerrada
    nome_tabela = extrair_texto(soup.find(id="lblNomeTabela"))
    if any(termo in nome_tabela.lower() for termo in ["serie encerrada", "série encerrada", "serie encerada", "série encerrada"]):
        return False, "Série encerrada", nome_tabela

    # 4. Verificar número de períodos existentes
    elemento_periodo = soup.find("span", id=lambda value: value and value.startswith("lblNomePeriodo"))
    periodicidade_info = elemento_periodo.text
    periodicidade_nome, num_periodos = periodicidade_info.split('(')
    periodicidade_nome = periodicidade_nome.strip()
    num_periodos = int(num_periodos.strip('):'))
    if num_periodos < 3:  # Verifica se o número de períodos é menor que 3
        return False, f"Períodos {num_periodos} < 3", nome_tabela  # Página 74 não deve cair aqui, pois possui 50 períodos
    
    # 4. Verificar última atualização e se ficou sem atualização por mais de três períodos
    ultima_atualizacao = extrair_texto(soup.find(id="lblDataAtualizacao"))  # Página 74 apresenta 'Última atualização: 2024-09-19 10:00:00'
    ultima_atualizacao_dt = pd.to_datetime(ultima_atualizacao, format='%Y-%m-%d %H:%M:%S', errors='coerce') if ultima_atualizacao else None
    if periodicidade_nome == 'Ano':
        frequencia_media_dias = 365.25
    elif periodicidade_nome == 'Biênio':
        frequencia_media_dias = 2 * 365.25
    elif periodicidade_nome == 'Mês':
        frequencia_media_dias = 365.25 / 12
    elif periodicidade_nome == 'Semestre':
        frequencia_media_dias = 365.25 / 2
    elif periodicidade_nome == 'Sexênio':
        frequencia_media_dias = 365.25 * 4
    elif periodicidade_nome == 'Trimestre':
        frequencia_media_dias = 365.25 / 4
    elif periodicidade_nome == 'Trimestre Móvel':
        frequencia_media_dias = 365.25 / 12
    elif periodicidade_nome == 'Triênio':
        frequencia_media_dias = 365.25 * 3
    else:
        frequencia_media_dias = 365.25 * 10  # decênio
    if ultima_atualizacao_dt is not None:
        dias_desde_atualizacao = (pd.to_datetime('today') - ultima_atualizacao_dt).days
        if dias_desde_atualizacao > 2.5 * frequencia_media_dias:
            return False, f"{ultima_atualizacao_dt.date()} < {frequencia_media_dias * 2.5 / (365.25 / 12)} meses para: {periodicidade_nome}", nome_tabela



    # 6. Verificar cobertura nacional e cobertura adequada
    niveis_territoriais = soup.find_all("span", id=lambda value: value and value.startswith("lstNiveisTerritoriais_lblIdNivelterritorial"))  # A página 74 apresenta múltiplos níveis territoriais, incluindo 'Brasil', 'Grande Região', 'Unidade da Federação', etc.
    cobertura_nacional = False
    cobertura = False
    for i, nivel in enumerate(niveis_territoriais):
        num_localidades_match = re.search(r'\((\d+)\)', extrair_texto(soup.find(id=f'lstNiveisTerritoriais_lblQuantidadeUnidadesTerritoriais_{i}')))  # Página 74 apresenta número de localidades como '(1)', '(5)', '(27)', etc.
        num_localidades = int(num_localidades_match.group(1)) if num_localidades_match else 0  # Valores extraídos da página 74 incluem 1, 5, 27, etc.
        nivel_id = extrair_texto(soup.find(id=f'lstNiveisTerritoriais_lblIdNivelterritorial_{i}'))  # Página 74 apresenta níveis como '1', '2', '3', '8', etc.
        nivel_id = f'N{nivel_id}'

        #nome_nivel = extrair_texto(soup.find(id=f'lstNiveisTerritoriais_lblNomeNivelterritorial_{i}'))  # Nomes dos níveis na página 74 incluem 'Brasil', 'Grande Região', 'Unidade da Federação'
        if localidades_totais_por_nivel[nivel_id]['cobertura_nacional']:
            cobertura_nacional = True
            if localidades_totais_por_nivel[nivel_id]['total'] * 0.8 <= num_localidades:
                cobertura = True
            
                if cobertura and cobertura_nacional:
                    break
    # 7. Verificar se a tabela tem nível territorial com cobertura nacional ou cobertura adequada
    if not cobertura_nacional:
        return False, "Sem nível territorial com cobertura nacional", nome_tabela

    # 8. Verificar se a cobertura é adequada
    if not cobertura:
        return False, f"Cobertura nacional menor que 80%.", nome_tabela  # Página 74 não deve cair aqui, pois possui cobertura adequada

    return True, f"Aprovado", nome_tabela  # Se todos os critérios forem atendidos, a tabela é aprovada


def atualizar_ibge():
    # Título do aplicativo
    st.title("Scraping de Tabelas do SIDRA IBGE")

    # Entrada para definir a tabela de início e fim
    tabela_inicio = st.number_input("Código da Tabela Inicial", min_value=1, value=1)
    tabela_fim = st.number_input("Código da Tabela Final", min_value=1, value=15000)

    # Nome do arquivo JSON para salvar os dados
    nome_arquivo = st.text_input("Nome do arquivo JSON para salvar", "tabelas_ibge.json")

    # Verificar se o arquivo já existe e perguntar se deseja sobrescrever ou mesclar os dados
    tabelas = {}
    if os.path.exists(nome_arquivo):
        opcao = st.radio("O arquivo já existe. Deseja sobrescrever ou mesclar os dados?", ("Sobrescrever", "Mesclar"))
        if opcao == "Mesclar":
            with open(nome_arquivo, "r", encoding="utf-8") as f:
                st.spinner('carregando tabelas')
                tabelas = json.load(f)
    
    # Botão para iniciar o scraping
    if st.button("Iniciar Scraping"):
        st.spinner('Inicializando Scraping')
        # Loop sobre o intervalo de tabelas especificado
        progress_text = 'Coletando dados'
        aprovados = 0
        my_bar = st.progress(0, text=progress_text)
        for cod_tabela in range(tabela_inicio, tabela_fim + 1):
            print('.', end='')
            url_tabela = f"https://apisidra.ibge.gov.br/desctabapi.aspx?c={cod_tabela}"
            soup = conectar(url_tabela)
            
            if soup:
                # Verificar se a tabela deve ser descartada ou aprovada
                aprovado, motivo, nome_tabela = aprovar_ou_reprovar(soup)
                my_bar.progress((cod_tabela + 1) / (tabela_fim + 1), text=f'`{cod_tabela}` - {nome_tabela}')
                if not aprovado:
                    st.toast(f"{cod_tabela}: {motivo}")
                    print(str(cod_tabela).rjust(6), motivo[:40].ljust(40), nome_tabela[:100])
                    continue
                else:
                    # Dicionário concentrando todas as transformações
                    tabela = {}
                    tabela.update(processar_metadados(soup, cod_tabela))
                    tabela['Níveis Territoriais'] = processar_niveis_territoriais(soup, cod_tabela)
                    tabela['Períodos'] = processar_periodos(soup)
                    tabela['Classificações'] = processar_classificacoes(soup)
                    tabela['Variáveis'] = processar_variaveis(soup)

                    # Adicionando novas estatísticas aos metadados
                    numero_localidades = sum(len(nivel.get("Localidades Presentes", {})) for nivel in tabela["Níveis Territoriais"].values())
                    numero_classificacoes = len(tabela["Classificações"])
                    numero_subclassificacoes = sum(len(classificacao.get("itens", {})) for classificacao in tabela["Classificações"].values())
                    numero_periodos = len(tabela["Períodos"].get("Lista de Períodos", {}))
                    numero_variaveis = len(tabela["Variáveis"])
                    subtabelas_totais = numero_localidades * (numero_subclassificacoes if numero_subclassificacoes else 1) * numero_variaveis
                    quantidade_valores = subtabelas_totais * numero_periodos
                    
                    for chave in ["Periodicidade", "Número de Períodos", "Data Mínima", "Data Máxima", "Intervalo Coberto (dias)", "Número de Registros", "Frequência Média (dias)", "Dias sem Registros até Hoje", 'Lista de Períodos']:
                        tabela[chave] = tabela['Períodos'][chave]
                    del tabela['Períodos']
                    #st.json(tabela, expanded=False)
                    
                    
                    tabela.update({
                        "Número de localidades": numero_localidades,
                        "Número de classificações": numero_classificacoes,
                        "Número de subclassificações": numero_subclassificacoes,
                        "Número de períodos": numero_periodos,
                        "Número de variáveis": numero_variaveis,
                        "Subtabelas totais": subtabelas_totais,
                        "Quantidade de valores": quantidade_valores
                    })

                    # Adicionando a tabela ao dicionário geral de tabelas
                    tabelas[cod_tabela] = tabela

                    # Salvando as tabelas em um arquivo JSON
                    with open(nome_arquivo, "w", encoding="utf-8") as f:
                        json.dump(tabelas, f, ensure_ascii=False, indent=4)

                # Exibir os metadados e variáveis gerados
                aprovados += 1
                st.success(f'`{cod_tabela}` - Aprovado N° `{aprovados}` - {nome_tabela}')
                print(str(cod_tabela).rjust(6), 'Aprovado N°', aprovados, nome_tabela[:50])
                st.toast(f'{cod_tabela} - Aprovado N° `{aprovados}`')
                

if __name__ == '__main__':
    st.set_page_config(layout='wide')
    atualizar_ibge()