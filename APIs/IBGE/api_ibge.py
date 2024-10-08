from echarts_plots import grafico_barras
import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import ast
from APIs.IBGE.filtros import aplicar_filtros
from APIs.IBGE.df_selecionavel import criar_dataframe_selecionavel
from APIs.IBGE.gerar_link_coletar_dados import gerar_link, coletar_dados
from APIs.IBGE.timeserie import gerar_timeserie

# Função principal
def api_ibge():
    st.title('API de Dados do IBGE')
    st.header('Selecione uma tabela abaixo')
    
    # Carregar os dados do CSV
    csv_file = "APIs/IBGE/metadados_tabelas.csv"
    df_metadados = pd.read_csv(csv_file, sep='\t', encoding='utf-8', index_col='Número')

    # Definir o índice do DataFrame como o código da tabela
    df_metadados.index.name = 'Código Tabela'

    # Converter colunas de listas de volta ao formato original
    df_metadados['Classificações'] = df_metadados['Classificações'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df_metadados['Variáveis'] = df_metadados['Variáveis'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df_metadados['Lista de Períodos'] = df_metadados['Lista de Períodos'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    for col in ['("N1", "Brasil")', '("N2", "Grande Região")', '("N3", "Unidade da Federação")', '("N6", "Município")']:
        if col in df_metadados.columns:
            df_metadados[col] = df_metadados[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

    # Armazenar os metadados originais para referência
    if 'df_metadados_original' not in st.session_state:
        st.session_state['df_metadados_original'] = df_metadados.copy()
    
    if 'df_metadados' not in st.session_state:
        st.session_state['df_metadados'] = df_metadados.copy()
    
    # Criação de variável antes das tabs para evitar duplicidade
    selecao_metadados = criar_dataframe_selecionavel(st.session_state['df_metadados'], 'Metadados das Tabelas', 'Selecione as Tabelas', 'df_metadados', hide_index=False)
    
    # Atualiza a variável sel_cod_tab com os códigos das tabelas selecionadas
    if selecao_metadados:
        st.session_state['sel_cod_tab'] = selecao_metadados
    else:
        st.session_state['sel_cod_tab'] = []
    
    # Botão para aplicar filtros
    if st.button("Aplicar Filtros"):
        aplicar_filtros(st.session_state['df_metadados'])
    
    # Verifica se apenas uma tabela foi selecionada
    if len(st.session_state['sel_cod_tab']) == 1:
        st.session_state['codigo_tabela'] = st.session_state['sel_cod_tab'][0]
    elif len(st.session_state['sel_cod_tab']) == 0:
        st.warning('Nenhuma tabela foi selecionada.')
    else:
        st.warning('Por favor, selecione apenas uma tabela.')
    
    if len(st.session_state['sel_cod_tab']) == 1:
        codigo_tabela = st.session_state['sel_cod_tab'][0]
        st.session_state['parametros_ibge'] = {
                            'codigo_tabela': codigo_tabela,
                            'variavel': None,
                            'classificacoes': [],
                            'nivel': None,
                            'localidade': None
                        }
        st.success(f"Tabela {codigo_tabela} selecionada")

        # Passo 2: Seleção de variáveis da API da tabela e exibição em formato de DataFrame selecionável
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            variaveis = st.session_state['df_metadados'].loc[codigo_tabela, 'Variáveis']
            if isinstance(variaveis, list) and len(variaveis) > 0:
                variaveis_data = []
                for variavel in variaveis:
                    codigo_variavel, nome_variavel = ast.literal_eval(variavel)
                    variaveis_data.append({'Código da Variável': codigo_variavel, 'Nome da Variável': nome_variavel})
                
                df_variaveis = pd.DataFrame(variaveis_data).set_index('Código da Variável')
                
                # Utilizando a função de DataFrame selecionável
                variavel_selecionada = criar_dataframe_selecionavel(df_variaveis, 'Variáveis', 'Selecione uma variável', 'variaveis')
                
                if variavel_selecionada:
                    variavel_escolhida = df_variaveis.loc[variavel_selecionada]  # Seleção de uma única variável
                    cod_variavel_escolhido = int(variavel_escolhida.index[0])
                    st.session_state['parametros_ibge']['variavel'] = cod_variavel_escolhido
            else:
                st.warning("Por favor, selecione uma variável.")

        with col2:
            # Passo 3: Carregar classificações e subclassificações da API
            classificacoes = st.session_state['df_metadados'].loc[codigo_tabela, 'Classificações']
            if isinstance(classificacoes, list) and len(classificacoes) > 0:
                classificacoes_dic = {}
                for classificacao in classificacoes:
                    ((cod_classificacao, nome_classificacao), (cod_subclassificacao, nome_subclassificacao)) = ast.literal_eval(classificacao)
                    cod_classificacao = int(cod_classificacao)
                    cod_subclassificacao = int(cod_subclassificacao)
                    classificacao_str = f'{cod_classificacao}: {nome_classificacao}'
                    if classificacao_str not in classificacoes_dic:
                        classificacoes_dic[classificacao_str] = []
                    classificacoes_dic[classificacao_str].append({'Código da Subclassificação': cod_subclassificacao, 'Nome da Subclassificação': nome_subclassificacao})
                for classificacao in classificacoes_dic:
                    cod_classificacao_escolhida = int(classificacao.split(':')[0])
                    df_classificacao = pd.DataFrame.from_dict(classificacoes_dic[classificacao]).set_index('Código da Subclassificação')
                    cod_subclassificacao_escolhida = criar_dataframe_selecionavel(df_classificacao, f'Classificação: `{classificacao}`', f'', f'classificacoes_{cod_classificacao}')
                    st.session_state['parametros_ibge']['classificacoes'].append([cod_classificacao_escolhida, cod_subclassificacao_escolhida[0]])
        

        with col3:
            # Seleção de nível territorial e localidade - Usando apenas os níveis disponíveis
            niveis_territoriais = []
            colunas = ['("N1", "Brasil")', '("N2", "Grande Região")', '("N3", "Unidade da Federação")', '("N6", "Município")']
            for column in colunas:
                if column in df_metadados.columns:
                    niveis_data = df_metadados.loc[codigo_tabela, column]
                    if isinstance(niveis_data, list) and len(niveis_data) > 0:
                        codigo_nivel_territorial, nome_nivel_territorial = ast.literal_eval(column)
                        niveis_territoriais.append({'Código do Nível Territorial': codigo_nivel_territorial, 'Nome do Nível Territorial': nome_nivel_territorial})
            
            if niveis_territoriais:
                df_niveis = pd.DataFrame(niveis_territoriais).set_index('Código do Nível Territorial')
                nivel_selecionado = criar_dataframe_selecionavel(df_niveis, 'Nível Territorial', 'Selecione um nível territorial', 'nivel_territorial')
                if nivel_selecionado:
                    st.session_state['parametros_ibge']['nivel'] = nivel_selecionado[0]
                    codigo_nivel_territorial = nivel_selecionado[0]
                    nivel = df_niveis.loc[codigo_nivel_territorial]
                    nome_nivel_territorial = nivel
                    string_coluna = f'("{codigo_nivel_territorial[:2]}", "{nome_nivel_territorial.values[0]}")'
                    localidades_data = st.session_state['df_metadados'].loc[codigo_tabela, string_coluna]
                    localidades_data = [{'Código da Localidade': int(eval(localidade)[0]), 'Nome da Localidade': eval(localidade)[-1]} for localidade in localidades_data]
                with col4:
                    if isinstance(localidades_data, list) and len(localidades_data) > 0:
                        #localidades_data = [{'Código da Localidade': loc[0], 'Nome da Localidade': loc[1]} for loc in localidades_data]
                        df_localidades = pd.DataFrame(localidades_data).set_index('Código da Localidade')
                        localidade_selecionada = criar_dataframe_selecionavel(df_localidades, f'Localidades para `{nivel_selecionado[0]}: {nome_nivel_territorial['Nome do Nível Territorial']}`', '', 'localidade')
                        if localidade_selecionada:
                            st.session_state['parametros_ibge']['localidade'] = localidade_selecionada[0]

        coletar = False
        with col5:
            # Exibir seleção
            selecao = pd.DataFrame([st.session_state['parametros_ibge']]).T
            selecao.columns = ['Seleção']

            # Ajustar o valor da coluna 'Seleção' para listas formatadas
            for index, row in selecao.iterrows():
                if isinstance(row['Seleção'], list):
                    selecao.at[index, 'Seleção'] = ', '.join(f"[{', '.join(map(str, item))}]" if isinstance(item, list) else str(item) for item in row['Seleção'])

            # Exibir o DataFrame no Streamlit
            st.dataframe(selecao, use_container_width=True)


            
        # Passo 5: Geração do link final e coleta de dados
        url = gerar_link()
        st.write('Link para os dados:')
        st.write(url)
        coletar = st.button("Coletar dados")
        coletar = True
        if coletar:
            
            
            st.write('')
            st.session_state['df_ibge'] = coletar_dados(url)
            if not st.session_state['df_ibge'].empty:
                st.dataframe(st.session_state['df_ibge'])
                st.success(f"Número de registros coletados: {len(st.session_state['df_ibge'])}")
                ts = gerar_timeserie()
                st.markdown(f'`{ts.columns[0]}`')
                
                # exibir a timeserie
                st.dataframe(ts, use_container_width=True)
                
                df_display = ts.copy()
                df_display.index = pd.to_datetime(df_display.index, format='%d/%m/%Y')
                
                # Converter o índice do DataFrame para datetime.datetime
                df_display.index = pd.to_datetime(df_display.index, format='%d/%m/%Y').to_pydatetime()
                
                nome_variavel = df_display.columns[0]
                
                # normalização
                if st.checkbox("Normalizar Dados", value=False):
                    # Converter o índice para datetime
                    df_display.iloc[:, 0] = (df_display.iloc[:, 0] - df_display.iloc[:, 0].min()) / (
                        df_display.iloc[:, 0].max() - df_display.iloc[:, 0].min()
                    )
                    grafico_barras(df_display, nome_variavel, key=nome_variavel + '-' + ' ibge')
                else:
                    grafico_barras(df_display, nome_variavel, key=nome_variavel + '-' + ' ibge')
                
                # enviar para pré-processamento
                if st.button("Enviar para Pré-processamento"):
                    # Verificar se já existe um DataFrame no pré-processamento
                    if 'df_original' in st.session_state and not st.session_state['df_original'].empty:
                        # Concatenar a nova série com as séries existentes
                        st.session_state['df_original'] = pd.concat([st.session_state['df_original'], ts.copy()], axis=1)
                    else:
                        # Se for a primeira série, apenas armazena
                        st.session_state['df_original'] = ts.copy()

                    st.success("Dados enviados para pré-processamento com sucesso!")

                    # Limpar df_concatenado para redefinir a página
                    st.session_state.df_concatenado = None

                #
            else:
                st.error('Erro na coleta dos dados.')
        
        
    else:
        st.warning('Por favor, selecione uma tabela na tab "Tabela".')
        

if __name__ == '__main__':
    # Configurar layout wide
    st.set_page_config(layout="wide")
    api_ibge()