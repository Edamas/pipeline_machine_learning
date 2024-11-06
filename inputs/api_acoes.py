# api_acoes.py

import streamlit as st
import pandas as pd
import yfinance as yf
from manager import series_manager
from datetime import datetime, timedelta

# Função para carregar e exibir o DataFrame selecionável para cada tipo de ativo
def exibir_dataframe_selecionavel(metadados, titulo):
    st.title("Fonte de Dados - Yahoo Finance")
    st.header(titulo)
    metadados.set_index('Símbolo', inplace=True)
    event = st.dataframe(
        metadados, 
        on_select='rerun', 
        selection_mode="multi-row", 
        use_container_width=True,
        column_config={
            'Visualização': st.column_config.AreaChartColumn(label="Visualização", width="medium", y_min=0, y_max=1,),
            'Data Mínima': st.column_config.DateColumn(format='DD/MM/YYYY'),
            'Data Máxima': st.column_config.DateColumn(format='DD/MM/YYYY'),
        }
    )
    selected_rows = event.selection.get('rows', [])
    return metadados.iloc[selected_rows].index.tolist()

# Funções para cada tipo de ativo
def crypto():
    metadados = pd.read_csv("inputs/metadados/CRYPTOCURRENCY.csv", sep='\t', encoding='utf-8')
    tickers = exibir_dataframe_selecionavel(metadados, "Criptomoedas")
    processar_tickers(tickers)

def currency():
    metadados = pd.read_csv("inputs/metadados/CURRENCY.csv", sep='\t', encoding='utf-8')
    tickers = exibir_dataframe_selecionavel(metadados, "Moedas")
    processar_tickers(tickers)

def equity():
    metadados = pd.read_csv("inputs/metadados/EQUITY.csv", sep='\t', encoding='utf-8')
    tickers = exibir_dataframe_selecionavel(metadados, "Ações")
    processar_tickers(tickers)

def etf():
    metadados = pd.read_csv("inputs/metadados/ETF.csv", sep='\t', encoding='utf-8')
    tickers = exibir_dataframe_selecionavel(metadados, "ETFs")
    processar_tickers(tickers)

def future():
    metadados = pd.read_csv("inputs/metadados/FUTURE.csv", sep='\t', encoding='utf-8')
    tickers = exibir_dataframe_selecionavel(metadados, "Futuros")
    processar_tickers(tickers)

def index():
    metadados = pd.read_csv("inputs/metadados/INDEX.csv", sep='\t', encoding='utf-8')
    tickers = exibir_dataframe_selecionavel(metadados, "Índices")
    processar_tickers(tickers)

def mutualfund():
    metadados = pd.read_csv("inputs/metadados/MUTUALFUND.csv", sep='\t', encoding='utf-8')
    tickers = exibir_dataframe_selecionavel(metadados, "Fundos Mútuos")
    processar_tickers(tickers)


# Função para obter dados históricos e processá-los
@st.cache_data(show_spinner=True)
def obter_dados_historicos(simbolo):
    from datetime import datetime

    data_atual = datetime.now()
    data_inicio = data_atual.replace(day=data_atual.day + 1, year=data_atual.year - 99)
    data_inicio_str, data_atual_str = data_inicio.strftime('%Y-%m-%d'), data_atual.strftime('%Y-%m-%d')

    # Tenta buscar histórico de 100 anos
    hist = pd.DataFrame()
    try:
        hist = yf.Ticker(simbolo).history(start=data_inicio_str, end=data_atual_str, interval='1d')
    except Exception:
        try:
            hist = yf.Ticker(simbolo).history(start=data_inicio_str, end=data_atual_str, interval='1wk')
        except Exception:
            try:
                hist = yf.Ticker(simbolo).history(start=data_inicio_str, end=data_atual_str, interval='1mo')
            except Exception:
                return hist

    if not hist.empty:
        hist.index = hist.index.tz_localize(None, ambiguous='NaT')  # Remove timezone
    return hist

# Função para processar múltiplos tickers
def processar_tickers(tickers):
    if tickers:
        # Inicializar df_main, df_original e df_editado, se já existirem no session_state
        if 'df_main' in st.session_state:
            st.session_state['df_original'] = st.session_state['df_main'].copy()
            st.session_state['df_editado'] = st.session_state['df_main'].copy()

        # Preparar o progresso e estado
        st.session_state['progress_bar_concluida'] = st.session_state.get('progress_bar_concluida', False)
        if not st.session_state['progress_bar_concluida']:
            progress_bar = st.progress(value=0, text='Carregando série(s) selecionada(s)')

        total_tickers = len(tickers)
        dados_acoes = {}
        series_com_erro = {}

        # Baixar dados para cada ticker usando obter_dados_historicos
        for idx, ticker in enumerate(tickers):
            try:
                df_acao = obter_dados_historicos(ticker)
                if df_acao.empty:
                    st.warning(f"Dados não disponíveis para {ticker}")
                    continue

                # Configuração da coluna de exibição
                colunas = df_acao.columns.tolist()
                coluna_selecionada = st.radio(
                    f'Selecione a coluna para `{ticker}`',
                    options=colunas,
                    horizontal=True,
                    index=min(4, len(colunas) - 1)
                )

                # Criação do nome da coluna com sufixo
                nome_coluna = f"{ticker}_{coluna_selecionada}"

                # Verifica se a coluna já existe e renomeia se necessário
                if nome_coluna in st.session_state['df_original'].columns:
                    st.warning(f"A coluna `{nome_coluna}` já existe. Dados não foram adicionados para evitar duplicação.")
                    continue

                # Adiciona a coluna com o nome modificado ao dicionário
                dados_acoes[nome_coluna] = df_acao[coluna_selecionada]
                st.write(f"Dados baixados para {ticker} - coluna `{coluna_selecionada}`")

                # Atualizar progressão do carregamento
                if not st.session_state['progress_bar_concluida']:
                    progress_bar.progress((idx + 1) / total_tickers, text=f'`{ticker}` - Carregado')

            except Exception as e:
                st.error(f"Erro ao baixar dados para {ticker}: {e}")
                series_com_erro[ticker] = str(e)

        # Atualizar df_editado com os dados coletados
        if dados_acoes:
            df_acoes = pd.DataFrame(dados_acoes)
            if 'df_main' in st.session_state:
                # Join com o DataFrame principal, evitando conflitos de nomes
                st.session_state['df_editado'] = st.session_state['df_main'].join(df_acoes, how='outer')
            else:
                st.session_state['df_editado'] = df_acoes
            st.session_state['df_original'] = st.session_state['df_editado'].copy()

        # Finalizar progresso
        if not st.session_state['progress_bar_concluida']:
            progress_bar.progress(1.0, text='Carregamento Concluído')
            st.session_state['progress_bar_concluida'] = True

        # Exibir erros
        for ticker, erro in series_com_erro.items():
            st.error(f"Erro ao carregar a série {ticker}: {erro}")

        # Chamar o gerenciador de séries
        series_manager()
    else:
        st.warning("Selecione ao menos um ativo.")
        series_manager()
        return
