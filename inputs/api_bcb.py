import streamlit as st
import pandas as pd
import requests
from manager import series_manager
from requests.exceptions import ConnectTimeout, HTTPError
import time

def autoridade_monetaria():
    st.title('Fonte de Dados')
    st.header("Autoridade Monetária")
    metadados = pd.read_csv("inputs/metadados/autoridade_monetaria.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)

def base_monetaria():
    st.title('Fonte de Dados')
    st.header("Autoridade Monetária")
    metadados = pd.read_csv("inputs/metadados/base_monetaria.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)

def cambio():
    st.title('Fonte de Dados')
    st.header("Câmbio")
    metadados = pd.read_csv("inputs/metadados/cambio.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)

def comercio_exterior():
    st.title('Fonte de Dados')
    st.header("Comércio Exterior")
    metadados = pd.read_csv("inputs/metadados/comercio_exterior.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)

def confianca_expectativas_metas():
    st.title('Fonte de Dados')
    st.header("Confiança, Expectativas e Metas")
    metadados = pd.read_csv("inputs/metadados/confianca_expectativas_metas.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)

def fatores_condicionantes_da_base_monetaria():
    st.title('Fonte de Dados')
    st.header("Fatores condicionantes da base Monetária")
    metadados = pd.read_csv("inputs/metadados/fatores_condicionantes_da_base_monetaria.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)

def industria_de_veiculos():
    st.title('Fonte de Dados')
    st.header("Indústria de Veículos")
    metadados = pd.read_csv("inputs/metadados/industria_de_veiculos.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)
    
def juros():
    st.title('Fonte de Dados')
    st.header("Juros")
    metadados = pd.read_csv("inputs/metadados/juros.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)
    
def mercado_de_trabalho():
    st.title('Fonte de Dados')
    st.header("Mercado de Trabalho")
    metadados = pd.read_csv("inputs/metadados/mercado_de_trabalho.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)
    
def poupanca():
    st.title('Fonte de Dados')
    st.header("Poupança")
    metadados = pd.read_csv("inputs/metadados/poupanca.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)

def precos_e_indices_gerais_inflacao():
    st.title('Fonte de Dados')
    st.header("Preços e Índices Gerais (Inflação)")
    metadados = pd.read_csv("inputs/metadados/precos_e_indices_gerais_inflacao.csv", sep='\t', encoding='utf-8')

def precos_e_indices_por_setor_inflacao():
    st.title('Fonte de Dados')
    st.header("Preços e Índices por Setor (Inflação)")
    metadados = pd.read_csv("inputs/metadados/precos_e_indices_por_setor_inflacao.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)

def regulacao_volatilidade_e_risco():
    st.title('Fonte de Dados')
    st.header("Regulação, Volatilidade e Risco")
    metadados = pd.read_csv("inputs/metadados/regulacao_volatilidade_e_risco.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)

def reservas_internacionais():
    st.title('Fonte de Dados')
    st.header("Reservas Internacionais")
    metadados = pd.read_csv("inputs/metadados/reservas_internacionais.csv", sep='\t', encoding='utf-8')
    api_bcb(metadados)

# Função para baixar dados com cache
@st.cache_data(show_spinner=True)
def baixar_bcb(codigo):
    url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json'
    try:
        response = requests.get(url)
    except:
        try:
            response = requests.get(url)
        except:
            response.raise_for_status()
    dados = response.json()
    if not dados:
        return None, "Erro: Dados vazios"
    return dados, "Sucesso"

def api_bcb(metadados):
    metadados = metadados[[col for col in metadados.columns if col not in ['categoria', 'name']]]
    metadados.set_index('código', inplace=True)
    metados = metadados.sort_values('popularidade', ascending=False).copy()
    
    # Seleção de múltiplas linhas
    event = st.dataframe(metadados, selection_mode="multi-row", on_select='rerun', use_container_width=True)
    selected_rows = event.selection.get('rows', [])

    series_selecionadas = {}
    
    # Inicializar df_original e df_editado com df_main, caso já existam dados
    if 'df_main' in st.session_state:
        st.session_state['df_original'] = st.session_state['df_main'].copy()
        st.session_state['df_editado'] = st.session_state['df_main'].copy()

    # Carregar séries selecionadas
    if not selected_rows:
        st.session_state['ha_selecao'] = False
    else:
        st.session_state['ha_selecao'] = True
        series_selecionadas = metadados.iloc[selected_rows]['nome'].to_dict()
        
        st.session_state['progress_bar_concluida'] = st.session_state.get('progress_bar_concluida', False)
        if not st.session_state['progress_bar_concluida']:
            # Inicializar o estado das séries selecionadas
            progress_bar = st.progress(value=0, text='Carregando série(s) selecionada(s)')
        total_series = len(series_selecionadas)
        series_com_erro = {}

        for idx, (codigo, nome_serie) in enumerate(series_selecionadas.items()):
            dados, status = baixar_bcb(codigo)  # Baixar a série
            if dados is not None:
                serie = pd.DataFrame(dados)
                serie['data'] = pd.to_datetime(serie['data'], format='%d/%m/%Y', dayfirst=True)
                serie['valor'] = pd.to_numeric(serie['valor'], errors='coerce')  # Garantir que os valores são numéricos
                serie.set_index('data', inplace=True)
                serie.rename(columns={'valor': nome_serie}, inplace=True)

                # Inicializando os dataframes
                if 'df_main' not in st.session_state:
                    st.session_state['df_main'] = pd.DataFrame()
                if 'df_original' not in st.session_state:
                    st.session_state['df_original'] = serie
                else:
                    st.session_state['df_original'] = st.session_state['df_original'].combine_first(serie)
                st.session_state['df_editado'] = st.session_state['df_original'].copy()

                # Inicializa os parâmetros no session_state
                dic_inicializar = {
                    f'data_min_{codigo}': serie.index.min(),
                    f'data_max_{codigo}': serie.index.max(),
                    f'normalizar_{codigo}': False,
                    f'ajustar_intervalo_comum_{codigo}': False,
                    }
                for chave, valor_inicial in dic_inicializar.items():
                    st.session_state[chave] = valor_inicial
            else:
                series_com_erro[codigo] = status

            # Atualiza o progresso da barra
            if not st.session_state['progress_bar_concluida']:
                progress_bar.progress((idx + 1) / total_series, text=f'`{codigo}` - `{nome_serie}`')
        if not st.session_state['progress_bar_concluida']:
            progress_bar.progress((idx + 1) / total_series, text=f'`[Carregamento Concluído]`')
            st.session_state['progress_bar_concluida'] = True
        # Mostrar mensagem de erro caso falhe
        for codigo, erro in series_com_erro.items():
            st.error(f"Erro ao carregar a série {codigo}: {erro}")

    series_manager()
