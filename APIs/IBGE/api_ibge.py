# api_ibge.py
import streamlit as st
import pandas as pd
import ast
from echarts_plots import grafico_barras
from APIs.IBGE.df_selecionavel import criar_dataframe_selecionavel
from APIs.IBGE.gerar_link_coletar_dados import gerar_link, coletar_dados
from APIs.IBGE.timeserie import gerar_timeserie
from APIs.send_to_analysis import send_to_analysis

@st.cache_data
def carregar_metadados():
    csv_file = "APIs/IBGE/metadados_tabelas.csv"
    df_metadados = pd.read_csv(csv_file, sep='\t', encoding='utf-8')
    df_metadados.set_index('Número', inplace=True)
    df_metadados.index.name = 'Código Tabela'
    df_metadados['Classificações'] = df_metadados['Classificações'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df_metadados['Variáveis'] = df_metadados['Variáveis'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df_metadados['Lista de Períodos'] = df_metadados['Lista de Períodos'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    for col in ['("N1", "Brasil")', '("N2", "Grande Região")', '("N3", "Unidade da Federação")', '("N6", "Município")']:
        if col in df_metadados.columns:
            df_metadados[col] = df_metadados[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    return df_metadados

@st.cache_data
def cache_coletar_dados(url):
    return coletar_dados(url)


def c1(codigo_tabela):
    variaveis = st.session_state['df_metadados'].loc[codigo_tabela, 'Variáveis']
    if isinstance(variaveis, list) and len(variaveis) > 0:
        variaveis_data = []
        for variavel in variaveis:
            codigo_variavel, nome_variavel = ast.literal_eval(variavel)
            variaveis_data.append({'Código da Variável': codigo_variavel, 'Nome da Variável': nome_variavel})
        df_variaveis = pd.DataFrame(variaveis_data).set_index('Código da Variável')
        variavel_selecionada = criar_dataframe_selecionavel(df_variaveis, 'Variáveis', 'Selecione uma variável', 'variaveis')
        if variavel_selecionada:
            variavel_escolhida = df_variaveis.loc[variavel_selecionada]
            cod_variavel_escolhido = int(variavel_escolhida.index[0])
            st.session_state['parametros_ibge']['variavel'] = cod_variavel_escolhido
    else:
        st.warning("Por favor, selecione uma variável.")


def c2(codigo_tabela):
    classificacoes = st.session_state['df_metadados'].loc[codigo_tabela, 'Classificações']
    if isinstance(classificacoes, list) and len(classificacoes) > 0:
        nao_ha_classificacoes = False
        classificacoes_dic = {}
        for classificacao in classificacoes:
            if '"' in classificacao:
                classificacao = classificacao.replace(', "', ", '''").replace('")', "''')")
            try:
                ((cod_classificacao, nome_classificacao), (cod_subclassificacao, nome_subclassificacao)) = ast.literal_eval(classificacao)
                cod_classificacao = int(cod_classificacao)
                cod_subclassificacao = int(cod_subclassificacao)
                classificacao_str = f'{cod_classificacao}: {nome_classificacao}'
                if classificacao_str not in classificacoes_dic:
                    classificacoes_dic[classificacao_str] = []
                classif_subclassif = {'Código da Subclassificação': cod_subclassificacao, 'Nome da Subclassificação': nome_subclassificacao}
                classificacoes_dic[classificacao_str].append(classif_subclassif)
            except Exception as e:
                st.error(f"Erro ao processar a classificação: {classificacao} - {e}")
                continue
        for classificacao in classificacoes_dic:
            cod_classificacao_escolhida = int(classificacao.split(':')[0])
            df_classificacao = pd.DataFrame.from_dict(classificacoes_dic[classificacao]).set_index('Código da Subclassificação')
            cod_subclassificacao_escolhida = criar_dataframe_selecionavel(df_classificacao, f'Classificação: `{classificacao}`', f'', f'classificacoes_{cod_classificacao}')
            if cod_subclassificacao_escolhida:
                st.session_state['parametros_ibge']['classificacoes'].append([cod_classificacao_escolhida, cod_subclassificacao_escolhida[0]])
    else:
        nao_ha_classificacoes = True
    return nao_ha_classificacoes


def c3(codigo_tabela):
    niveis_territoriais = []
    colunas = ['("N1", "Brasil")', '("N2", "Grande Região")', '("N3", "Unidade da Federação")', '("N6", "Município")']
    for column in colunas:
        if column in st.session_state['df_metadados'].columns:
            niveis_data = st.session_state['df_metadados'].loc[codigo_tabela, column]
            if isinstance(niveis_data, list) and len(niveis_data) > 0:
                codigo_nivel_territorial, nome_nivel_territorial = ast.literal_eval(column)
                niveis_territoriais.append({'Código do Nível Territorial': codigo_nivel_territorial, 'Nome do Nível Territorial': nome_nivel_territorial})

    localidades_data = []
    if isinstance(niveis_territoriais, list) and len(niveis_territoriais) > 0:
        df_niveis = pd.DataFrame(niveis_territoriais).set_index('Código do Nível Territorial')
        nivel_selecionado = criar_dataframe_selecionavel(df_niveis, 'Nível Territorial', 'Selecione um nível territorial', 'nivel_territorial')
        if nivel_selecionado:
            st.session_state['parametros_ibge']['nivel'] = nivel_selecionado[0]
            codigo_nivel_territorial = nivel_selecionado[0]
            if codigo_nivel_territorial == 'N1':  # Selecionar automaticamente 'Brasil' para nível territorial Brasil
                st.session_state['parametros_ibge']['localidade'] = 1
            else:
                nivel = df_niveis.loc[codigo_nivel_territorial]
                nome_nivel_territorial = nivel
                string_coluna = f'("{codigo_nivel_territorial[:2]}", "{nome_nivel_territorial.values[0]}")'
                string_coluna = string_coluna.replace('- Brasil - Brasil', '- Brasil')
                if string_coluna in st.session_state['df_metadados'].columns:
                    localidades_data = st.session_state['df_metadados'].loc[codigo_tabela, string_coluna]
                    localidades_data = [{'Código da Localidade': int(eval(localidade)[0]), 'Nome da Localidade': eval(localidade)[-1]} for localidade in localidades_data]

    if isinstance(localidades_data, list) and len(localidades_data) > 0:
        df_localidades = pd.DataFrame(localidades_data).set_index('Código da Localidade')
        localidade_selecionada = criar_dataframe_selecionavel(df_localidades, f'Localidades para `{nivel_selecionado[0]}: {nome_nivel_territorial["Nome do Nível Territorial"]}`', '', 'localidade')
        if localidade_selecionada:
            st.session_state['parametros_ibge']['localidade'] = localidade_selecionada[0]


def c4():
    selecao = pd.DataFrame([st.session_state['parametros_ibge']]).T
    selecao.columns = ['Seleção']
    for index, row in selecao.iterrows():
        if isinstance(row['Seleção'], list):
            selecao.at[index, 'Seleção'] = ', '.join(map(str, row['Seleção']))
        elif isinstance(row['Seleção'], int):
            selecao.at[index, 'Seleção'] = str(row['Seleção'])
    st.dataframe(selecao, use_container_width=True)


def api_ibge():
    st.title('API de Dados do IBGE')
    st.header('Selecione uma tabela abaixo')
    df_metadados = carregar_metadados()
    if 'df_metadados' not in st.session_state:
        st.session_state['df_metadados'] = df_metadados.copy()
    selecao_metadados = criar_dataframe_selecionavel(st.session_state['df_metadados'], 'Metadados das Tabelas', 'Selecione as Tabelas', 'df_metadados', hide_index=False)
    if selecao_metadados:
        st.session_state['sel_cod_tab'] = selecao_metadados
    else:
        st.session_state['sel_cod_tab'] = []

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
        col1, col2, col3, col4 = st.columns(4)
        with col1:            c1(codigo_tabela)  # Seleção de variáveis
        with col2:            
            nao_ha_classificacoes = c2(codigo_tabela)  # Seleção de classificações
        with col3:            c3(codigo_tabela)  # Seleção de níveis territoriais e localidades
        with col4:            c4()  # Exibir resumo da seleção

        # Coleta de dados e envio para análise
        if st.session_state['parametros_ibge']['codigo_tabela'] and \
           st.session_state['parametros_ibge']['variavel'] and \
           (st.session_state['parametros_ibge']['classificacoes'] or nao_ha_classificacoes) and \
           st.session_state['parametros_ibge']['nivel'] and \
           st.session_state['parametros_ibge']['localidade']:

            url = gerar_link()
            st.write('Link para os dados selecionados:')
            st.write(url)
            st.write('')
            st.session_state['df_ibge'] = cache_coletar_dados(url)

            if not st.session_state['df_ibge'].empty:
                st.session_state['df_ibge']['Valor'] = pd.to_numeric(st.session_state['df_ibge']['Valor'], errors='coerce')
                st.session_state['df_ibge'].dropna(subset=['Valor'], inplace=True)
                st.dataframe(st.session_state['df_ibge'])

                registros_validos = st.session_state['df_ibge']['Valor'].count()
                if registros_validos == 0:
                    st.error('Nenhum dado numérico retornado para a série selecionada.')
                else:
                    st.write(f"Número de registros válidos coletados: {registros_validos}")

                    # Gerar timesérie e exibir gráfico
                    ts = gerar_timeserie()
                    ts.columns = [col.replace('Brasil - Brasil', '- Brasil') for col in ts.columns]
                    st.header(ts.columns[0])
                    st.dataframe(ts, use_container_width=True)
                    df_display = ts.copy()
                    df_display.index = pd.to_datetime(df_display.index, errors='coerce', dayfirst=True)

                    nome_variavel = df_display.columns[0]
                    if st.checkbox("Normalizar Dados", value=False):
                        df_display.iloc[:, 0] = (df_display.iloc[:, 0] - df_display.iloc[:, 0].min()) / (df_display.iloc[:, 0].max() - df_display.iloc[:, 0].min())

                    grafico_barras(df_display, colunas=[nome_variavel], key=nome_variavel + '-' + 'ibge')

                    # Adicione uma chave ao session_state para gerenciar o envio
                    if 'enviar_para_analise_ibge' not in st.session_state:
                        st.session_state.enviar_para_analise_ibge = False

                    # Botão de envio para análise
                    if st.button("Enviar para Análise", key="enviar_para_analise_unico_ibge"):
                        # Defina que a série foi solicitada para envio
                        st.session_state.enviar_para_analise_ibge = True

                    # Se o botão foi clicado, ou seja, se o estado de envio está marcado como True
                    if st.session_state.enviar_para_analise_ibge:
                        sucesso = send_to_analysis(ts)
                        if sucesso:
                            # Limpar o estado de envio se bem-sucedido
                            st.session_state.enviar_para_analise_ibge = False
                        else:
                            # Em caso de erro, manter True para que o usuário possa tentar novamente
                            st.session_state.enviar_para_analise_ibge = True

                        
    else:
        st.warning('Por favor, selecione apenas uma tabela.')

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    api_ibge()
