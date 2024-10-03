from datetime import datetime 
import streamlit as st
import pandas as pd
from APIs.IBGE.funcoes_ibge import (carregar_dados, criar_dataframe_selecionavel, aplicar_filtro_por_codigos_tabelas, obter_variaveis, obter_classificacoes_subclassificacoes, exibir_classificacoes_subclassificacoes, selecionar_niveis_localidades, gerar_link_coletar_dados, gerar_timeserie)
from echarts_plots import grafico_barras, grafico_linhas, grafico_scatterplot, grafico_candlestick, grafico_violin  # Importações das funções de gráfico


# Função principal
def api_ibge():
    st.title('API de Dados do IBGE')
    st.header('Selecione uma tabela abaixo')
    
    if 'df_metadados' not in st.session_state:
        carregar_dados()
    
    # Criação de variável antes das tabs para evitar duplicidade
    selecao_metadados = criar_dataframe_selecionavel(st.session_state['df_metadados'], 'Metadados das Tabelas', 'Selecione as Tabelas', 'df_metadados', hide_index=False)
    
    
    # Se a seleção foi feita, atualiza a variável sel_cod_tab com os códigos das tabelas selecionadas
    if selecao_metadados:
        st.session_state['sel_cod_tab'] = [st.session_state['df_metadados'].index[i] for i in selecao_metadados]
    else:
        st.session_state['sel_cod_tab'] = st.session_state.get('sel_cod_tab', st.session_state['df_metadados'].index.tolist()) or st.session_state['df_metadados'].index.tolist()
    
    tab1, tab2, tab3 = st.tabs(['Tabela', 'Parâmetros', 'Dados'])

    # Conteúdo de tab1
    with tab1:
        col1, col2, col3 = st.columns([4, 1, 1])
        # Exibe o número de tabelas filtradas (com base na seleção)
        col2.metric(label="Tabelas Filtradas", value=len(st.session_state['sel_cod_tab']))
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
                        st.session_state['sel_cod_tab'] = list(set(st.session_state['sel_cod_tab']) & set(codigos_tabelas_status))

                # Filtros de Assunto, Pesquisa e Fonte
                col_assunto, col_pesquisa, col_fonte = st.columns(3)

                with col_assunto:
                    df_assunto_unico = st.session_state['df_metadados'][['Assunto']].drop_duplicates().reset_index(drop=True)
                    selecoes_assunto = criar_dataframe_selecionavel(df_assunto_unico, 'Assuntos', 'Selecione o(s) assunto(s).', 'df_assunto', col_assunto, hide_index=True)
                    if selecoes_assunto:
                        valores_selecionados_assunto = df_assunto_unico.iloc[selecoes_assunto]['Assunto'].tolist()
                        codigos_tabelas_assunto = st.session_state['df_metadados'].loc[st.session_state['df_metadados']['Assunto'].isin(valores_selecionados_assunto)].index.tolist()
                        st.session_state['sel_cod_tab'] = list(set(st.session_state['sel_cod_tab']) & set(codigos_tabelas_assunto))

                with col_pesquisa:
                    df_pesquisa_unico = st.session_state['df_metadados'][['Pesquisa']].drop_duplicates().reset_index(drop=True)
                    selecoes_pesquisa = criar_dataframe_selecionavel(df_pesquisa_unico, 'Pesquisa', 'Selecione a(s) pesquisa(s).', 'df_pesquisa', col_pesquisa, hide_index=True)
                    if selecoes_pesquisa:
                        valores_selecionados_pesquisa = df_pesquisa_unico.iloc[selecoes_pesquisa]['Pesquisa'].tolist()
                        codigos_tabelas_pesquisa = st.session_state['df_metadados'].loc[st.session_state['df_metadados']['Pesquisa'].isin(valores_selecionados_pesquisa)].index.tolist()
                        st.session_state['sel_cod_tab'] = list(set(st.session_state['sel_cod_tab']) & set(codigos_tabelas_pesquisa))

                with col_fonte:
                    df_fonte_unico = st.session_state['df_metadados'][['Fonte']].drop_duplicates().reset_index(drop=True)
                    selecoes_fonte = criar_dataframe_selecionavel(df_fonte_unico, 'Fonte', 'Selecione a(s) fonte(s).', 'df_fonte', col_fonte, hide_index=True)
                    if selecoes_fonte:
                        valores_selecionados_fonte = df_fonte_unico.iloc[selecoes_fonte]['Fonte'].tolist()
                        codigos_tabelas_fonte = st.session_state['df_metadados'].loc[st.session_state['df_metadados']['Fonte'].isin(valores_selecionados_fonte)].index.tolist()
                        st.session_state['sel_cod_tab'] = list(set(st.session_state['sel_cod_tab']) & set(codigos_tabelas_fonte))

                # Filtros de Níveis, Periodicidade, e Períodos
                col_niveis, col_periodicidade, col_periodos = st.columns(3)

                with col_niveis:
                    df_niveis = st.session_state['df_niveis'][st.session_state['df_niveis']['Código Nível'].isin(st.session_state['rel_tabelaXniveis'][st.session_state['rel_tabelaXniveis']['Código Tabela'].isin(st.session_state['df_metadados'].index)]['Código Nível'])]
                    selecoes_niveis = criar_dataframe_selecionavel(df_niveis, 'Níveis Territoriais', 'Selecione o Nível Territorial', 'df_niveis', col_niveis, hide_index=True)
                    if selecoes_niveis:
                        valores_selecionados_niveis = df_niveis.iloc[selecoes_niveis][df_niveis.columns[0]].tolist()
                        rel_niveis = st.session_state['rel_tabelaXniveis'][st.session_state['rel_tabelaXniveis']['Código Nível'].isin(valores_selecionados_niveis)]
                        codigos_tabelas_niveis = rel_niveis['Código Tabela'].unique()
                        st.session_state['sel_cod_tab'] = list(set(st.session_state['sel_cod_tab']) & set(codigos_tabelas_niveis))

                with col_periodicidade:
                    df_periodicidade = st.session_state['df_periodicidade'][st.session_state['df_periodicidade']['Código Periodicidade'].isin(
                        st.session_state['rel_tabelaXperiodicidade'][st.session_state['rel_tabelaXperiodicidade']['Código Tabela'].isin(
                            st.session_state['df_metadados'].index)]['Código Periodicidade'])]
                    selecoes_periodicidade = criar_dataframe_selecionavel(df_periodicidade, 'Periodicidade', 'Selecione a Periodicidade', 'df_periodicidade', col_periodicidade, hide_index=True)
                    if selecoes_periodicidade:
                        valores_selecionados_periodicidade = df_periodicidade.iloc[selecoes_periodicidade][df_periodicidade.columns[0]].tolist()
                        rel_periodicidade = st.session_state['rel_tabelaXperiodicidade'][st.session_state['rel_tabelaXperiodicidade']['Código Periodicidade'].isin(valores_selecionados_periodicidade)]
                        codigos_tabelas_periodicidade = rel_periodicidade['Código Tabela'].unique()
                        st.session_state['sel_cod_tab'] = list(set(st.session_state['sel_cod_tab']) & set(codigos_tabelas_periodicidade))

                with col_periodos:
                    df_periodos = st.session_state['df_periodos'][st.session_state['df_periodos']['Código Período'].isin(
                        st.session_state['rel_tabelaXperiodos'][st.session_state['rel_tabelaXperiodos']['Código Tabela'].isin(
                            st.session_state['df_metadados'].index)]['Código Período'])]
                    selecoes_periodos = criar_dataframe_selecionavel(df_periodos, 'Períodos', 'Selecione os Períodos', 'df_periodos', col_periodos, hide_index=True)
                    if selecoes_periodos:
                        valores_selecionados_periodos = df_periodos.iloc[selecoes_periodos][df_periodos.columns[0]].tolist()
                        rel_periodos = st.session_state['rel_tabelaXperiodos'][st.session_state['rel_tabelaXperiodos']['Código Período'].isin(valores_selecionados_periodos)]
                        codigos_tabelas_periodos = rel_periodos['Código Tabela'].unique()
                        st.session_state['sel_cod_tab'] = list(set(st.session_state['sel_cod_tab']) & set(codigos_tabelas_periodos))

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
                        st.session_state['sel_cod_tab'] = list(set(st.session_state['sel_cod_tab']) & set(codigos_tabelas_variaveis))

                with col_classificacoes:
                    df_classificacoes = st.session_state['df_classificacoes'][st.session_state['df_classificacoes']['Código Classificação'].isin(
                        st.session_state['rel_tabelaXclassificacoes'][st.session_state['rel_tabelaXclassificacoes']['Código Tabela'].isin(
                            st.session_state['df_metadados'].index)]['Código Classificação'])]
                    selecoes_classificacoes = criar_dataframe_selecionavel(df_classificacoes, 'Classificações', 'Selecione as Classificações', 'df_classificacoes', col_classificacoes, hide_index=True)
                    if selecoes_classificacoes:
                        valores_selecionados_classificacoes = df_classificacoes.iloc[selecoes_classificacoes][df_classificacoes.columns[0]].tolist()
                        rel_classificacoes = st.session_state['rel_tabelaXclassificacoes'][st.session_state['rel_tabelaXclassificacoes']['Código Classificação'].isin(valores_selecionados_classificacoes)]
                        codigos_tabelas_classificacoes = rel_classificacoes['Código Tabela'].unique()
                        st.session_state['sel_cod_tab'] = list(set(st.session_state['sel_cod_tab']) & set(codigos_tabelas_classificacoes))

                with col_subclassificacoes:
                    df_subclassificacoes = st.session_state['df_subclassificacoes'][st.session_state['df_subclassificacoes']['Código Subclassificação'].isin(
                        st.session_state['rel_tabelaXsubclassificacoes'][st.session_state['rel_tabelaXsubclassificacoes']['Código Tabela'].isin(
                            st.session_state['df_metadados'].index)]['Código Subclassificação'])]
                    selecoes_subclassificacoes = criar_dataframe_selecionavel(df_subclassificacoes, 'Subclassificações', 'Selecione as Subclassificações', 'df_subclassificacoes', col_subclassificacoes, hide_index=True)
                    if selecoes_subclassificacoes:
                        valores_selecionados_subclassificacoes = df_subclassificacoes.iloc[selecoes_subclassificacoes][df_subclassificacoes.columns[0]].tolist()
                        rel_subclassificacoes = st.session_state['rel_tabelaXsubclassificacoes'][st.session_state['rel_tabelaXsubclassificacoes']['Código Subclassificação'].isin(valores_selecionados_subclassificacoes)]
                        codigos_tabelas_subclassificacoes = rel_subclassificacoes['Código Tabela'].unique()
                        st.session_state['sel_cod_tab'] = list(set(st.session_state['sel_cod_tab']) & set(codigos_tabelas_subclassificacoes))

        if aplicar_filtros:
            # Aplica o filtro por códigos selecionados
            for key in ['df_metadados']:
                aplicar_filtro_por_codigos_tabelas(key, st.session_state['sel_cod_tab'])
            st.rerun()  # Reexecuta a aplicação após aplicar os filtros

        # Botão para resetar filtros
        if resetar_filtros:
            carregar_dados()  # Recarrega os dados originais
            st.session_state['sel_cod_tab'] = st.session_state['df_metadados'].index.tolist()  # Inicializa com todos os códigos de tabela
            st.session_state['dados_ibge_coletados'] = False
            st.session_state['df_ibge_temp'] = pd.DataFrame()
            st.rerun()

        # Verifica se apenas uma tabela foi selecionada
        if len(st.session_state['sel_cod_tab']) == 1:
            st.session_state['codigo_tabela'] = st.session_state['sel_cod_tab'][0]
            st.success(f'Tabela {st.session_state["sel_cod_tab"][0]} selecionada. Clique na tab "Parâmetros"')
        elif len(st.session_state['sel_cod_tab']) == 0:
            st.warning('Nenhuma tabela foi selecionada.')
        else:
            st.warning('Por favor, selecione apenas uma tabela.')
        
    with tab2:
        if len(st.session_state['sel_cod_tab']) == 1:
            codigo_tabela = st.session_state['sel_cod_tab'][0]
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
                resultado_niveis = selecionar_niveis_localidades(codigo_tabela)

                # Verificar se o retorno foi de dois valores
                if resultado_niveis and len(resultado_niveis) == 2:
                    nivel, localidade = resultado_niveis  # Apenas nível e localidade
                else:
                    nivel, localidade, df_localidades = resultado_niveis  # Nível, localidade e DataFrame

                if nivel and localidade:
                    st.write(f'Nível territorial selecionado: {nivel}')
                    st.write(f'Localidade selecionada: {localidade}')
                    st.session_state['parametros_ibge'] = {
                        'codigo_tabela': codigo_tabela,
                        'nome_tabela': st.session_state['df_metadados'].loc[codigo_tabela, 'Nome Tabela'],
                        'variavel': df_variaveis.loc[variavel_selecionada, 'Nome Variável'].values[0].split(' - casas decimais')[0],
                        'nivel': nivel,
                        'localidade': df_localidades.loc[localidade, 'Nome'] if df_localidades is not None else localidade,
                        }

                    # Passo 5: Geração do link final e coleta de dados
                    if st.button("Coletar dados"):
                        st.session_state['df_ibge_temp'] = gerar_link_coletar_dados(codigo_tabela, variavel_escolhida, selecoes_classificacoes, nivel, localidade)
                        if not st.session_state['df_ibge_temp'].empty:
                            st.success('Dados coletados com sucesso! Clique na tab Dados.')
                        else:
                            st.error('Erro na coleta dos dados.')
                else:
                    st.warning("Por favor, selecione um nível territorial e uma localidade.")
            else:
                st.warning("Por favor, selecione uma variável.")
        else:
            st.warning('Por favor, selecione uma tabela na tab "Tabela".')
    
    with tab3:
        if 'df_ibge_temp' in st.session_state:
            if not st.session_state['df_ibge_temp'].empty:
                st.success('Dados coletados!')
                st.dataframe(st.session_state['df_ibge_temp'], use_container_width=True)
                st.session_state['ts_ibge_temp'] = gerar_timeserie(st.session_state['df_ibge_temp'])
                
                # Verificar se a série temporal foi gerada corretamente
                if 'ts_ibge_temp' in st.session_state and not st.session_state['ts_ibge_temp'].empty:
                    
                    ts_ibge_temp = st.session_state['ts_ibge_temp'].copy()
                    
                    ts_ibge_temp.set_index('data', inplace=True)
                    if ts_ibge_temp.index.name != 'data':
                        ts_ibge_temp.set_index('data', inplace=True)
                    
                    # Configurando o nome da coluna de Valor com base nos 'parametros_ibge' utilizados
                    if 'parametros_ibge' in st.session_state:
                        parametros_ibge = st.session_state['parametros_ibge']
                        st.write(parametros_ibge)
                        nome_variavel = f"{parametros_ibge.get('variavel')} - {parametros_ibge.get('nome_tabela')} - {parametros_ibge.get('localidade')}"
                    else:
                        st.error("'parametros_ibge' não encontrado no session_state.")
                        nome_variavel = 'Valor'
                    ts_ibge_temp.columns = [nome_variavel]
                    
                    # Converte o índice para datetime (caso ainda não esteja)
                    #ts_ibge_temp.index = pd.to_datetime(ts_ibge_temp.index)
                    
                    # Exibir a série temporal
                    st.session_state['ts_ibge_temp'] = ts_ibge_temp.copy()
                    ts_ibge_temp.index = pd.to_datetime(ts_ibge_temp.index, format='%d/%m/%Y')  # Convertendo para datetime no formato desejado

                    st.dataframe(ts_ibge_temp, use_container_width=True)  # data em formato correto

                    # Adicionar a opção para normalizar os dados
                    normalizar = st.toggle("Normalizar Dados", value=False)

                    # Criar uma cópia do DataFrame para normalização, se necessário
                    if normalizar:
                        df_normalizado = st.session_state['ts_ibge_temp'].copy()
                        df_normalizado.iloc[:, 0] = (df_normalizado.iloc[:, 0] - df_normalizado.iloc[:, 0].min()) / (df_normalizado.iloc[:, 0].max() - df_normalizado.iloc[:, 0].min())
                        # Exibir gráfico com a série temporal usando ECharts
                        grafico_barras(df_normalizado, st.session_state['ts_ibge_temp'].columns[0], key=st.session_state['ts_ibge_temp'].columns[0] + '-' + ' ibge')
                    else:
                        # Exibir gráfico com a série temporal usando ECharts
                        grafico_barras(st.session_state['ts_ibge_temp'], ts_ibge_temp.columns[0], key=st.session_state['ts_ibge_temp'].columns[0] + '-' + ' ibge')

                    
                    
                    # Botão para enviar para pré-processamento
                    if st.button("Enviar para Pré-processamento"):
                        if 'df_original' in st.session_state and nome_variavel in st.session_state['df_original'].columns:
                            st.warning("Série temporal já presente no pré-processamento. Nada adicionado.")
                        else:
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
                st.error('O dataframe df_ibge_temp está vazio')
        else:
            st.warning('Dados não coletados. Certifique-se de selecionar uma tabela e especificar os parâmetros da consulta.')

if __name__ == '__main__':
    # Configurar layout wide
    st.set_page_config(layout="wide")
    api_ibge()
