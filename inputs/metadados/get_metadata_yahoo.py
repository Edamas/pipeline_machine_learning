import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os

# Função para gerar e limpar duplicatas de tickers
@st.cache_data(show_spinner=True)
def gerar_tickers():
    file = 'inputs/metadados/SymbolName_selected.csv'
    ticker_symbols = pd.read_csv(file, sep='\t', encoding='utf-8')
    ticker_symbols = ticker_symbols.drop_duplicates('Símbolo')
    return ticker_symbols

# Função para obter e traduzir metadados de um ticker
@st.cache_data(show_spinner=True)
def obter_metadados(simbolo):
    yf_ticker = yf.Ticker(simbolo)
    info = yf_ticker.info
    
    if not info or ((len(info) == 1 and 'trailingPegRatio' in info)):
        return None
    elif not info.get('quoteType', None):
        return None

    info_traduzido = {traducoes.get(k, k): v for k, v in info.items()}
    info_traduzido['Símbolo'] = simbolo
    return info_traduzido

# Função para obter dados históricos e processá-los
@st.cache_data(show_spinner=True)
def obter_dados_historicos(simbolo, info):
    data_atual = datetime.now()
    data_inicio = data_atual.replace(day=data_atual.day + 1, year=data_atual.year - 99)
    data_inicio_str, data_atual_str = data_inicio.strftime('%Y-%m-%d'), data_atual.strftime('%Y-%m-%d')

    # Tenta buscar histórico de 100 anos
    hist = pd.DataFrame()
    try:
        hist = yf.Ticker(simbolo).history(start=data_inicio_str, end=data_atual_str, interval='1d')
    except Exception as e:
        try:
            hist = yf.Ticker(simbolo).history(start=data_inicio_str, end=data_atual_str, interval='1wk')
        except Exception as ee:
            try:
                hist = yf.Ticker(simbolo).history(start=data_inicio_str, end=data_atual_str, interval='1mo')
            except Exception as eee:
                try:
                    hist = yf.Ticker(simbolo).history(start=data_inicio_str, end=data_atual_str)
                except Exception as eeee:
                    info['Série Ativa'] = False
                    return info
    if hist.empty:
        info['Série Ativa'] = False
        return info
    
    # Normaliza o índice de datas para remover timezone
    hist.index = hist.index.tz_localize(None, ambiguous='NaT')

    # Resample mensal e normalização dos valores
    hist = hist.resample('ME').last()
    precos_coluna = hist['Adj Close'] if 'Adj Close' in hist else hist['Close']
    min_valor, max_valor = precos_coluna.min(), precos_coluna.max()

    # Normaliza o preço e armazena a visualização como lista
    info['Visualização'] = list(((precos_coluna - min_valor) / (max_valor - min_valor)).ffill().round(3))
    info['Data Mínima'] = hist.index.min()
    info['Data Máxima'] = hist.index.max()
    
    # Verifica atualizações recentes e quantidade de registros
    if info['Data Máxima'] < (pd.Timestamp.now() - timedelta(days=180)):
        info['Série Ativa'] = False
    elif len(info['Visualização']) <= 6:
        info['Série Ativa'] = False
    elif min_valor == max_valor:
        info['Série Ativa'] = False
    else:
        info['Série Ativa'] = True
    info['Colunas'] = list(hist.columns)
    return info

# Função principal para coleta e processamento de dados
def get_yahoo_metadata():
    st.subheader("Módulo para Captura de Dados do Yahoo Finance")
    tickers_df = gerar_tickers()
    
    tipos_de_ativos = ['TODOS']
    for tipo in tickers_df['Tipo de Ativo'].unique():
        tipos_de_ativos.append(tipo)
    tipo_selecionado = st.radio('Selecione o Tipo de Ativo', options=tipos_de_ativos, index=None, horizontal=True)
    if tipo_selecionado != 'TODOS' and tipo_selecionado:
        tickers_df = tickers_df.loc[tickers_df['Tipo de Ativo'] == tipo_selecionado].copy()
    st.write(f"Total de Tickers para coleta: `{len(tickers_df)}`")
    # Seleção de séries pelo usuário
    selected_rows = st.dataframe(tickers_df, on_select='rerun', key='tickers', use_container_width=True)
    selected_rows = selected_rows['selection']['rows']
    
    if not selected_rows:
        st.info("Selecione pelo menos um ticker para visualizar os metadados.")
    else:
        tickers_selecionados = tickers_df.iloc[selected_rows]
        metadados_dict = {}  # Dicionário para armazenar os dados de cada símbolo
        
        with st.status('Carregando metadados', expanded=True):
            for _, ticker in tickers_selecionados.iterrows():
                simbolo = ticker['Símbolo']
                
                # Coleta e traduz metadados
                info_traduzido = obter_metadados(simbolo)
                if info_traduzido and 'Símbolo' in info_traduzido:
                    info_traduzido = obter_dados_historicos(simbolo, info_traduzido)
                    if info_traduzido and 'Série Ativa' in info_traduzido:
                        if info_traduzido['Série Ativa']:
                            metadados_dict[simbolo] = info_traduzido  # Armazena no dicionário
                            cols = st.columns(4)
                            cols[0].success('Dados coletados') 
                            cols[1].success(simbolo)
                            cols[2].success(info_traduzido.get('Nome Abreviado', simbolo))
                            cols[3].success(':blue[Série Ativa]')
                        else:
                            cols = st.columns(4)
                            cols[0].error('Dados não coletados') 
                            cols[1].error(simbolo)
                            cols[2].error(info_traduzido.get('Nome Abreviado', simbolo))
                            cols[3].error(':red[Série Inativa]')
                    else:
                        continue
                else:
                    continue
        
        # Converte o dicionário final em DataFrame para salvar ou apresentar
        df_metadados = pd.DataFrame.from_dict(metadados_dict, orient='index')
        
        df_metadados.index.name = 'Símbolo'

        # Traduz e reorganiza colunas com base no dicionário de tradução
        #df_metadados.rename(columns=traducoes, inplace=True)
        colunas_ordenadas = []
        for col in traducoes.values():
            if col in df_metadados.columns and col not in colunas_ordenadas:
                colunas_ordenadas.append(col)
        for col in df_metadados.columns:
            if col not in traducoes.values() and col not in colunas_ordenadas:
                colunas_ordenadas.append(col)
        df_metadados = df_metadados[colunas_ordenadas]
        df_metadados.set_index('Símbolo', inplace=True)
        metadados_file = 'inputs/metadados/yf_metadados.csv'
        df_metadados.to_csv(metadados_file, sep='\t', encoding='utf-8')
        # Exibição por Tipo de Ativo com colunas configuradas
        if 'Tipo de Ativo' in df_metadados.columns and 'Série Ativa' in df_metadados.columns:
            df_metadados = df_metadados.loc[df_metadados['Série Ativa'] == True].copy()
            tipos_de_ativos = df_metadados['Tipo de Ativo'].unique()
            for tipo_de_ativo in tipos_de_ativos:
                with st.expander(f"Dados de {tipo_de_ativo}", expanded=True):
                    df_por_tipo = df_metadados[df_metadados['Tipo de Ativo'] == tipo_de_ativo]
                    df_por_tipo = df_por_tipo.dropna(axis=1, how='all')

                    st.dataframe(
                        data=df_por_tipo,
                        column_config={
                            'Visualização': st.column_config.AreaChartColumn(label="Visualização", width="medium", y_min=0, y_max=1),
                            'Data Mínima': st.column_config.DateColumn(format='DD/MM/YYYY'),
                            'Data Máxima': st.column_config.DateColumn(format='DD/MM/YYYY'),
                        }
                    )
                    df_por_tipo.to_csv(f'inputs/metadados/{tipo_de_ativo.upper()}.csv', sep='\t', encoding='utf-8')
                    #st.code(tipo_de_ativo + '\n' + '\n'.join(column for column in df_por_tipo.columns.tolist()))


# Dicionário de tradução
traducoes = {
    # campos comuns
    'symbol': 'Símbolo',
    # Identificação da área
    'name': 'Nome',
    'shortName': 'Nome Abreviado',
    'longName': 'Nome Completo',
    
    'quoteType': 'Tipo de Ativo',
    'sector': 'Setor',
    'industry': 'Indústria',
    
    'Data Mínima': 'Data Mínima',
    'Data Máxima': 'Data Máxima',
    'visualization': 'Visualização',
    
    
    'longBusinessSummary': 'Sumário de Negócios',
    'description': 'Descrição',
    'currency': 'Moeda',
    'exchange': 'Exchange',
    'country': 'País',
    
    # análises
    'morningStarOverallRating': 'Avaliação Geral Morning Star',
    'morningStarRiskRating': 'Avaliação de Risco Morning Star',
    'auditRisk': 'Risco de Auditoria',
    'boardRisk': 'Risco do Conselho',
    'compensationRisk': 'Risco de Compensação',
    'shareHolderRightsRisk': 'Risco de Direitos dos Acionistas',
    'overallRisk': 'Risco Geral',
    'startDate': 'Data de Início',
    
    # preços
    'marketCap': 'Capitalização de Mercado',
    'totalRevenue': 'Receita Total',
    'volumeAllCurrencies': 'Volume em Todas as Moedas',
    'circulatingSupply': 'Oferta Circulante',
    'underlyingSymbol': 'Símbolo Subjacente',
    'regularMarketOpen': 'Abertura Regular',  
    'firstTradeDateEpochUtc': 'Data do Primeiro Negócio (UTC)',
    'priceHint': 'Dica de Preço',
    'open': 'Abertura',
    'previousClose': 'Fechamento Anterior',
    'dayLow': 'Mínimo do Dia',
    'dayHigh': 'Máximo do Dia',
    'regularMarketPreviousClose': 'Fechamento Regular Anterior',
    'regularMarketDayLow': 'Mínimo do Dia Regular',
    'regularMarketDayHigh': 'Máximo do Dia Regular',
    'volume': 'Volume',
    'regularMarketVolume': 'Volume Regular',
    'averageVolume': 'Volume Médio',
    'averageVolume10days': 'Volume Médio dos Últimos 10 Dias',
    'averageDailyVolume10Day': 'Volume Diário Médio dos Últimos 10 Dias',
    'fiftyTwoWeekLow': 'Mínimo em 52 Semanas',
    'fiftyTwoWeekHigh': 'Máximo em 52 Semanas',
    'fiftyDayAverage': 'Média de 50 Dias',
    'twoHundredDayAverage': 'Média de 200 Dias',
    'fromCurrency': 'Moeda de Origem',
    'toCurrency': 'Moeda de Destino',
    'lastMarket': 'Último Mercado',
    'coinMarketCapLink': 'Link do CoinMarketCap',
    'volume24Hr': 'Volume em 24 Horas',
    'ask': 'Preço de Venda (ask)',
    'bid': 'Preço de Compra (bid)',
    
    
    'Colunas': 'Colunas Presentes', 
    
    # endereço
    'address1': 'Endereço 1',
    'address2': 'Endereço 2',
    'address3': 'Endereço 3',
    'city': 'Cidade',
    'state': 'Estado',
    'zip': 'CEP',
    
    # sites
    'website': 'Website',
    
    'messageBoardId': 'ID do Quadro de Mensagens',
    'trailingPegRatio': 'Razão de Atrelamento Retrospectivo',
    'maxAge': 'Idade Máxima',
    
    
    
    'fullTimeEmployees': 'Funcionários em Tempo Integral',
    
    'governanceEpochDate': 'Data da Governança',
    'dividendRate': 'Taxa de Dividendos',
    'dividendYield': 'Rendimento de Dividendos',
    'exDividendDate': 'Data Ex-Dividendo',
    'payoutRatio': 'Índice de Distribuição de Dividendos',
    'fiveYearAvgDividendYield': 'Rendimento Médio de Dividendos em 5 Anos',
    'beta': 'Beta (beta)',
    'trailingPE': 'Preço/Lucro por Ação (P/L) Retrospectivo (trailing P/E)',
    'forwardPE': 'Preço/Lucro por Ação (P/L) Futuro (forward P/E)',
    'debtToEquity': 'Dívida sobre Patrimônio',
    'revenuePerShare': 'Receita por Ação',
    'returnOnAssets': 'Retorno sobre Ativos',
    'returnOnEquity': 'Retorno sobre Patrimônio',
    'freeCashflow': 'Fluxo de Caixa Livre',
    'operatingCashflow': 'Fluxo de Caixa Operacional',
    'revenueGrowth': 'Crescimento da Receita',
    'grossMargins': 'Margens Brutas',
    'ebitdaMargins': 'Margens EBITDA',
    'operatingMargins': 'Margens Operacionais',
    'financialCurrency': 'Moeda Financeira',
    'currentPrice': 'Preço Atual',
    'targetHighPrice': 'Preço-Alvo Máximo',
    'targetLowPrice': 'Preço-Alvo Mínimo',
    'targetMeanPrice': 'Preço-Alvo Médio',
    'targetMedianPrice': 'Preço-Alvo Mediano',
    'recommendationMean': 'Recomendação Média',
    'recommendationKey': 'Chave de Recomendação',
    'numberOfAnalystOpinions': 'Número de Opiniões de Analistas',
    'totalCash': 'Total de Caixa',
    'totalCashPerShare': 'Total de Caixa por Ação',
    'ebitda': 'Lucros antes de Juros, Impostos, Depreciação e Amortização (EBITDA)',
    'totalDebt': 'Dívida Total',
    'quickRatio': 'Razão Rápida',
    'currentRatio': 'Razão Corrente',
    'twitter': 'X (ex-Twitter)',
    'phone': 'Telefone',
    'companyOfficers': 'Executivos da Empresa',
    'compensationAsOfEpochDate': 'Compensação em Data Epoch',
    'bidSize': 'Tamanho do Lote de Compra',
    'askSize': 'Tamanho do Lote de Venda',
    'priceToSalesTrailing12Months': 'Preço sobre Vendas (12 Meses)',
    'enterpriseValue': 'Valor da Empresa',
    'grossProfits': 'Lucro Bruto',
    'profitMargins': 'Margens de Lucro',
    'floatShares': 'Ações em Circulação',
    'sharesOutstanding': 'Ações Emitidas',
    'sharesShort': 'Ações em Posse Curta',
    'sharesShortPriorMonth': 'Ações em Posse Curta do Mês Anterior',
    'sharesShortPreviousMonthDate': 'Data das Ações em Posse Curta do Mês Anterior',
    'dateShortInterest': 'Data do Interesse Curto',
    'sharesPercentSharesOut': 'Porcentagem de Ações em Posse Curta',
    'heldPercentInsiders': 'Porcentagem de Ações Retidas por Insiders',
    'heldPercentInstitutions': 'Porcentagem de Ações Retidas por Instituições',
    'shortRatio': 'Relação Curta',
    'shortPercentOfFloat': 'Porcentagem de Float Curto',
    'impliedSharesOutstanding': 'Ações Emitidas Implícitas',
    'bookValue': 'Valor Contábil',
    'priceToBook': 'Preço sobre o Valor Contábil',
    'lastFiscalYearEnd': 'Data de Fim do Último Ano Fiscal',
    'nextFiscalYearEnd': 'Data de Fim do Próximo Ano Fiscal',
    'mostRecentQuarter': 'Último Trimestre',
    'earningsQuarterlyGrowth': 'Crescimento de Lucros Trimestrais',
    'netIncomeToCommon': 'Renda Líquida para Ações Ordinárias',
    'trailingEps': 'EPS Retrospectivo (trailing EPS)',
    'forwardEps': 'EPS Futuro (forward EPS)',
    'pegRatio': 'Razão PEG (PEG Ratio)',
    'lastSplitFactor': 'Fator do Último Desdobramento',
    'lastSplitDate': 'Data do Último Desdobramento (split)',
    'enterpriseToRevenue': 'Valor da Empresa sobre Receita',
    'enterpriseToEbitda': 'Valor da Empresa sobre EBITDA',
    '52WeekChange': 'Mudança em 52 Semanas',
    'SandP52WeekChange': 'Mudança do S&P em 52 Semanas',
    'gmtOffSetMilliseconds': 'Offset GMT em Milissegundos',
    'earningsGrowth': 'Crescimento dos Lucros',
    'irWebsite': 'Website de Relações com Investidores',
    'trailingAnnualDividendRate': 'Taxa de Dividendo Anual Retrospectiva',
    'trailingAnnualDividendYield': 'Rendimento de Dividendo Anual Retrospectivo',
    'lastDividendValue': 'Último Valor de Dividendo',
    'lastDividendDate': 'Data do Último Dividendo',
    'expireDate': 'Data de Expiração',
    'openInterest': 'Interesse Aberto',
    'yield': 'Rendimento',
    'totalAssets': 'Ativos Totais',
    'navPrice': 'Preço da Cota (NAV)',
    'category': 'Categoria',
    'ytdReturn': 'Retorno de um Ano (YTD)',
    'beta3Year': 'Beta (3 Anos)',
    'fundFamily': 'Família do Fundo',
    'legalType': 'Tipo Legal',
    'threeYearAverageReturn': 'Retorno Médio em 3 Anos',
    'fiveYearAverageReturn': 'Retorno Médio em 5 Anos',
    'annualHoldingsTurnover': 'Rotatividade de Holdings Anuais',
    'fax': 'Fax',
    'Ativo': 'Ativo',
    
    'fundInceptionDate': 'Data de Início do Fundo',
    
    'sectorKey': 'Chave do Setor',
    'industryKey': 'Chave da Indústria',
    
    'sectorDisp': 'Setor (Exibido)',
    'industryDisp': 'Indústria (Exibido)',
    
    'industrySymbol': 'Símbolo da Indústria',
    
    
    
    'timeZoneFullName': 'Nome Completo do Fuso Horário',
    'timeZoneShortName': 'Nome Abreviado do Fuso Horário',
    'uuid': 'UUID',    
    

}

if __name__ == "__main__":
    st.set_page_config(layout='wide')
    get_yahoo_metadata()
