# api_bcb.py

import streamlit as st
import pandas as pd
import requests
import os
from inputs.send_to_analysis import send_to_analysis

# Função para baixar dados com cache
@st.cache_data(show_spinner=False)
def baixar_dados_serie(codigo):
    url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.text.strip() == "":
            return None, "Erro: Resposta vazia da API"
        dados = response.json()
        if not dados:
            return None, "Erro: Dados vazios"
        df = pd.DataFrame(dados)
        if df.empty:
            return None, "Erro: DataFrame vazio"
        # Converter 'data' para datetime no formato 'dd/mm/aaaa'
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', dayfirst=True)
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        return df, "Sucesso"
    except Exception as e:
        return None, f"Erro ao baixar série: {e}"

def api_page_bcb():
    st.title("API: Banco Central do Brasil")

    # Caminho do arquivo CSV
    metadados_path = os.path.join("inputs", "BANCO_CENTRAL", "BCB_metadata_active.csv")

    # Tente carregar o CSV em um DataFrame
    try:
        metadados = pd.read_csv(metadados_path)
        dados_filtrados = metadados
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado: {metadados_path}")
        dados_filtrados = pd.DataFrame()  # DataFrame vazio como fallback

    event = st.dataframe(dados_filtrados, selection_mode="multi-row", on_select="rerun")
    selected_rows = event.selection.get('rows', []) if event.selection else []

    series_selecionadas = []
    if selected_rows:
        for idx in selected_rows:
            idx = int(idx)
            serie_info = dados_filtrados.iloc[idx]
            series_selecionadas.append({
                "nome": serie_info["nome"],
                "codigo": serie_info["código"],
                "frequencia": serie_info["frequencia"]
            })
        st.json(series_selecionadas)

    # Inicializar variáveis de estado da sessão
    if 'df_concatenado' not in st.session_state:
        st.session_state.df_concatenado = None

    if selected_rows and st.button("Carregar Séries Selecionadas"):
        df_concatenado = None
        total_series = len(series_selecionadas)
        progresso = 0
        progresso_barra = st.progress(0)
        with st.spinner("Baixando dados das séries selecionadas..."):
            for serie in series_selecionadas:
                baixar_dados_serie.clear()
                df_serie, status = baixar_dados_serie(serie["codigo"])
                progresso += 1
                progresso_barra.progress(progresso / total_series)
                if df_serie is None:
                    st.error(f"Erro ao carregar série {serie['codigo']} - {serie['nome']}: {status}. Favor carregar novamente.")
                else:
                    # Verificar se as colunas 'data' e 'valor' existem
                    if 'data' in df_serie.columns and 'valor' in df_serie.columns:
                        # Renomear a coluna 'valor' para o nome da série
                        df_serie.rename(columns={'valor': serie['nome']}, inplace=True)
                        df_serie = df_serie.set_index('data')
                    else:
                        st.error(f"Série {serie['codigo']} - {serie['nome']} não possui as colunas necessárias. Favor carregar novamente.")
                        continue

                    num_registros = df_serie.shape[0]
                    st.success(f"Série {serie['codigo']} - {serie['nome']} carregada com sucesso. Registros: {num_registros}")

                    # Concatenar as séries usando merge
                    if df_concatenado is None:
                        df_concatenado = df_serie
                    else:
                        df_concatenado = df_concatenado.merge(df_serie, left_index=True, right_index=True, how='outer')

        if df_concatenado is not None and not df_concatenado.empty:
            # Ordenar o índice e nomeá-lo como 'data'
            df_concatenado.sort_index(inplace=True)
            df_concatenado.index.name = 'data'

            # Armazenar o DataFrame concatenado na sessão
            st.session_state.df_concatenado = df_concatenado

    # Verificar se o DataFrame está disponível
    if st.session_state.df_concatenado is not None and not st.session_state.df_concatenado.empty:
        df_concatenado = st.session_state.df_concatenado.copy()

        # Exibir gráfico com opções
        st.subheader("Gráfico das Séries Carregadas")
        colunas_disponiveis = df_concatenado.columns.tolist()
        colunas_selecionadas = st.multiselect(
            "Selecione as séries para exibir no gráfico",
            colunas_disponiveis,
            default=colunas_disponiveis,
            key='colunas_grafico'
        )

        normalizar = st.checkbox("Normalizar dados", value=False, key='normalizar_checkbox')

        if colunas_selecionadas:
            df_plot = df_concatenado[colunas_selecionadas].copy()
            if normalizar:
                df_plot = (df_plot - df_plot.min()) / (df_plot.max() - df_plot.min())

            # Garantir que o índice é datetime e formatado corretamente (sem horário)
            df_plot.index = pd.to_datetime(df_plot.index, errors='coerce').normalize()

            st.line_chart(df_plot)
        else:
            st.warning("Selecione ao menos uma série para exibir o gráfico.")

        # Exibir DataFrame
        st.subheader("Dados das Séries Carregadas")
        df_display = df_concatenado.copy()

        # Garantir que o índice é datetime e formatado corretamente (sem horário)
        df_display.index = pd.to_datetime(df_display.index, errors='coerce', dayfirst=True).strftime('%d/%m/%Y')

        st.dataframe(df_display)

        if 'enviar_para_analise_bcb' not in st.session_state:
            st.session_state.enviar_para_analise_bcb = False

        if st.button("Enviar para Análise", key="enviar_para_analise_unico_bcb"):
            st.session_state.enviar_para_analise_bcb = True

        if st.session_state.enviar_para_analise_bcb:
            sucesso = send_to_analysis(df_concatenado)


if __name__ == '__main__':
    st.set_page_config(layout="wide")
    api_page_bcb()
