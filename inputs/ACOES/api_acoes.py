import streamlit as st
import pandas as pd
import yfinance as yf

# Grupos de ações principais (nacional e internacional)
acoes_nacionais = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA', 'BBAS3.SA', 'GGBR4.SA', 'ITSA4.SA']
acoes_internacionais = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'FB', 'NVDA', 'JPM', 'V', 'DIS', 'NFLX']

# Função para obter os metadados completos de um ticker
def obter_metadados_ticker(ticker):
    try:
        ticker_info = yf.Ticker(ticker).info
        return ticker_info
    except Exception as e:
        st.error(f"Erro ao obter metadados para {ticker}: {e}")
        return None

# Função para carregar os dados das ações e metadados
def carregar_dados_acoes(tickers, mostrar_metadados_completos):
    dados_metadados = []

    for ticker in tickers:
        metadados = obter_metadados_ticker(ticker)
        if metadados:
            if mostrar_metadados_completos:
                # Reorganizar para garantir que 'shortName' (nome da empresa) esteja como o primeiro campo
                metadados_reordenados = {
                    "Company Name": metadados.get('shortName', 'N/A'),  # Primeiro campo: Nome da empresa
                    **{k: v for k, v in metadados.items() if k != 'shortName'}  # Outros metadados
                }
                dados_metadados.append(metadados_reordenados)
            else:
                dados_metadados.append({
                    "Company Name": metadados.get('shortName', 'N/A')  # Apenas o nome da empresa
                })

    # Criar um dataframe com os metadados
    df_metadados = pd.DataFrame(dados_metadados, index=tickers)  # Definir o ticker como índice
    return df_metadados

# Função principal da API
def api_acoes():
    st.title("API de Ações - Yahoo Finance")

    # Tickers a serem usados para obter os metadados (seleção principal)
    tickers_principais = acoes_nacionais + acoes_internacionais

    # Input para adicionar ticker manualmente
    novo_ticker = st.text_input("Adicionar novo ticker:", max_chars=5)  # Limite de caracteres para tickers
    if st.button("Adicionar Ticker"):
        if novo_ticker:
            tickers_principais.append(novo_ticker)
        else:
            st.warning("Digite um ticker válido.")

    # Filtros
    col1, col2, col3, col4 = st.columns(4)

    # Toggle para exibir todos os metadados ou apenas o nome da companhia
    mostrar_metadados_completos = col1.toggle("Exibir todos os metadados", value=False)

    # Multiselect para nacional/internacional
    filtro_nacionalidade = col2.multiselect(
        "Filtrar por nacionalidade",
        ['Nacional', 'Internacional'],
        default=['Nacional', 'Internacional']
    )

    # Filtro adicional 1
    filtro_adicional_1 = col3.multiselect("Filtro Adicional 1", ['Setor 1', 'Setor 2', 'Setor 3'], default=['Setor 1', 'Setor 2', 'Setor 3'])

    # Filtro adicional 2
    filtro_adicional_2 = col4.multiselect("Filtro Adicional 2", ['Tipo 1', 'Tipo 2', 'Tipo 3'], default=['Tipo 1', 'Tipo 2', 'Tipo 3'])

    # Aplicar filtros de nacionalidade
    if 'Nacional' not in filtro_nacionalidade:
        tickers_principais = [t for t in tickers_principais if t not in acoes_nacionais]
    if 'Internacional' not in filtro_nacionalidade:
        tickers_principais = [t for t in tickers_principais if t not in acoes_internacionais]

    # Carregar todos os metadados das ações selecionadas
    df_metadados = carregar_dados_acoes(tickers_principais, mostrar_metadados_completos)

    # Exibir dataframe principal com os metadados ou apenas o nome da companhia
    if not df_metadados.empty:
        st.write("Tabela Principal:")
        st.dataframe(df_metadados, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os tickers selecionados.")

if __name__ == '__main__':
    st.set_page_config(layout='wide')
    api_acoes()
