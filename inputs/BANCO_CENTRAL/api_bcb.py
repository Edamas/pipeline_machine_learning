# inputs.BANCO_CENTRAL.api_bcb.py
import streamlit as st
import pandas as pd
import requests
from inputs.send_to_analysis import send_to_analysis

# Função para baixar dados com cache
@st.cache_data(show_spinner=False)
def baixar_dados_serie(codigo):
    url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        dados = response.json()
        if not dados:
            return None, "Erro: Dados vazios"
        df = pd.DataFrame(dados)
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', dayfirst=True)
        # Mantém valores nulos e converte corretamente valores válidos em int/float
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        return df, "Sucesso"
    except Exception as e:
        return None, f"Erro ao baixar série: {e}"

# Função para limpar o cache de uma série
def limpar_cache_serie(codigo):
    baixar_dados_serie.clear()

def api_page_bcb():
    st.title("API: Banco Central do Brasil")

    metadados_path = "inputs/BANCO_CENTRAL/BCB_metadata_active.csv"
    try:
        metadados = pd.read_csv(metadados_path)
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado: {metadados_path}")
        return

    # Armazenar as séries carregadas com sucesso e com erro
    if 'series_carregadas' not in st.session_state:
        st.session_state['series_carregadas'] = {}
    if 'series_com_erro' not in st.session_state:
        st.session_state['series_com_erro'] = {}

    # Exibir a tabela para seleção
    event = st.dataframe(metadados, selection_mode="multi-row", on_select="rerun")
    selected_rows = event.selection.get('rows', []) if event.selection else []

    series_selecionadas = []
    if selected_rows:
        series_selecionadas = metadados.iloc[selected_rows][['nome', 'código', 'frequencia']].to_dict('records')

        # Coluna 1: Exibir seleção como dataframe
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.subheader("Seleção")
            selecao_df = pd.DataFrame(series_selecionadas)
            st.dataframe(selecao_df, use_container_width=True)

        # Coluna 2: Status do carregamento
        with col2:
            st.subheader("Carregamento")
            progresso_total = st.progress(0)
            progresso_por_serie = {}
            total_series = len(series_selecionadas)

            for idx, serie in enumerate(series_selecionadas):
                codigo = serie['código']
                nome = serie['nome']

                # Exibir progresso individual para cada série
                if codigo not in progresso_por_serie:
                    progresso_por_serie[codigo] = st.empty()

                if codigo not in st.session_state['series_carregadas'] and codigo not in st.session_state['series_com_erro']:
                    with progresso_por_serie[codigo].container():
                        st.write(f"Baixando série {nome} ({codigo})...")
                        progresso_individual = st.progress(0)

                        df_serie, status = baixar_dados_serie(codigo)
                        if df_serie is None:
                            st.session_state['series_com_erro'][codigo] = serie
                            progresso_por_serie[codigo].error(f"Erro: {status}")
                        else:
                            df_serie.rename(columns={'valor': nome}, inplace=True)
                            df_serie.set_index('data', inplace=True)
                            st.session_state['series_carregadas'][codigo] = df_serie
                            progresso_por_serie[codigo].success(f"Série {nome} ({codigo}) carregada com sucesso.")
                    
                progresso_total.progress((idx + 1) / total_series)

        # Remover séries desmarcadas
        codigos_atuais = [serie['código'] for serie in series_selecionadas]
        for codigo in list(st.session_state['series_carregadas'].keys()):
            if codigo not in codigos_atuais:
                # Remover do cache e da sessão
                limpar_cache_serie(codigo)
                del st.session_state['series_carregadas'][codigo]

        # Se houver séries carregadas
        if st.session_state['series_carregadas']:
            ts = pd.concat(st.session_state['series_carregadas'].values(), axis=1)
            ts.sort_index(inplace=True)
            ts.index.name = 'data'
            ts.index = pd.to_datetime(ts.index, format='%d/%m/%Y')

            # Coluna 3: Visualização
            with col3:
                st.subheader("Visualização")
                colunas_disponiveis = ts.columns.tolist()
                colunas_selecionadas = st.multiselect("Seleção das séries para visualização", colunas_disponiveis, default=colunas_disponiveis)

                if colunas_selecionadas:
                    normalizar_visualizacao = st.checkbox("Normalizar dados apenas para visualização")
                    min_data = ts.index.min().date()
                    max_data = ts.index.max().date()
                    
                    slider_data = st.slider("Filtrar intervalo de datas apenas para visualização", min_value=min_data, max_value=max_data, value=(min_data, max_data))
                    ts_temp = ts.loc[pd.to_datetime(slider_data[0]):pd.to_datetime(slider_data[1]), colunas_selecionadas]

                    if normalizar_visualizacao:
                        ts_temp = (ts_temp - ts_temp.min()) / (ts_temp.max() - ts_temp.min())

            # Coluna 4: Envio para análise
            with col4:
                st.subheader("Envio")
                aplicar_normalizacao_envio = st.checkbox("Aplicar normalização ao enviar para análise", value=False)
                aplicar_filtro_envio = st.checkbox("Aplicar filtro de intervalo de datas para enviar para análise", value=False)
                aplicar_selecionadas_envio = st.checkbox("Aplicar apenas as séries selecionadas para análise", value=False, disabled=(len(colunas_selecionadas) == len(colunas_disponiveis)))

                if aplicar_normalizacao_envio:
                    ts_enviar = (ts_temp - ts_temp.min()) / (ts_temp.max() - ts_temp.min())
                else:
                    ts_enviar = ts_temp.copy()

                if aplicar_filtro_envio:
                    ts_enviar = ts_temp

                if aplicar_selecionadas_envio:
                    ts_enviar = ts_enviar[colunas_selecionadas]

                df_enviada = pd.DataFrame()
                if st.button("Enviar para Análise"):
                    df_enviada = send_to_analysis(ts_enviar)

            # Abaixo das colunas: DataFrame e Gráfico
            col5, col6 = st.columns(2)

            with col5:
                if df_enviada.empty:
                    with st.expander("Dados das Séries Carregadas"):
                        st.dataframe(ts_temp, use_container_width=True)
                else:
                    with st.expander("Dados das Séries Enviadas"):
                        st.dataframe(df_enviada, use_container_width=True)

            with col6:
                with st.expander("Gráfico das Séries Carregadas"):
                    st.line_chart(ts_temp, use_container_width=True)

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    api_page_bcb()
