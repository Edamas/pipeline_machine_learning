import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from preprocessing.null_handling import tratar_nulos
from preprocessing.normalization import normalizar
from preprocessing.date_handling import preencher_datas_faltantes
from preprocessing.column_calculations import calcular_novas_colunas

def pre_processing_page(df_series):
    st.title("Pré-Processamento de Dados")

    if df_series:
        serie_selecionada = st.selectbox("Selecione a Série para Pré-Processamento", list(df_series.keys()))
        df_original = df_series[serie_selecionada]
        
        # Verificar se já existe uma cópia pré-processada
        if f"df_preprocessed_{serie_selecionada}" not in st.session_state:
            st.session_state[f"df_preprocessed_{serie_selecionada}"] = df_original.copy()

        df = st.session_state[f"df_preprocessed_{serie_selecionada}"]

        # Tab para exibir dados e gráficos
        tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Visão Geral e Estatísticas", "Manipular Datas", "Tratar Nulos", 
            "Normalizar Dados", "Codificar Categorias", 
            "Calcular Novas Colunas", "Salvar e Reverter"
        ])

        with tab0:
            st.subheader("Dados da Série Selecionada")
            st.dataframe(df)
            
            st.subheader("Estatísticas Descritivas")
            st.write(df.describe())

            st.subheader("Gráficos das Colunas")
            colunas_graficos = st.multiselect("Selecione as colunas para exibir os gráficos", df.columns)
            for coluna in colunas_graficos:
                st.line_chart(df[coluna])

        with tab1:
            st.subheader("Manipular Datas e Configurar Período de Interesse")
            coluna_data = st.selectbox("Selecione a coluna de Data", df.columns, index=df.columns.get_loc("data") if "data" in df.columns else 0)

            frequencia = st.radio("Selecione a frequência", ["Não Alterar", "Diária", "Mensal", "Anual"], index=0)
            if frequencia != "Não Alterar" and st.button("Aplicar Regularização de Datas"):
                df = preencher_datas_faltantes(df, freq=frequencia, coluna_data=coluna_data)
                st.session_state[f"df_preprocessed_{serie_selecionada}"] = df
                st.success("Regularização de datas aplicada com sucesso!")

            data_inicio = st.date_input("Data de Início", value=df[coluna_data].min())
            data_fim = st.date_input("Data de Fim", value=df[coluna_data].max())

            if st.button("Aplicar Período de Interesse"):
                df = df[(df[coluna_data] >= pd.to_datetime(data_inicio)) & (df[coluna_data] <= pd.to_datetime(data_fim))]
                st.session_state[f"df_preprocessed_{serie_selecionada}"] = df
                st.success("Período de interesse aplicado com sucesso!")

        with tab2:
            st.subheader("Tratar Nulos")
            estrategia_nulos = st.radio("Escolha como tratar valores nulos", 
                                        ["Não Alterar", "Remover Nulos", "Preencher com Zero", "Preencher com Último Valor"], index=0)
            coluna_valor = st.selectbox("Selecione a coluna de valor para tratar nulos", df.columns)
            if estrategia_nulos != "Não Alterar" and st.button("Aplicar Tratamento de Nulos"):
                df[coluna_valor] = tratar_nulos(df[coluna_valor], estrategia_nulos)
                st.session_state[f"df_preprocessed_{serie_selecionada}"] = df
                st.success("Tratamento de nulos aplicado!")

        with tab3:
            st.subheader("Normalizar Dados")
            tipo_normalizacao = st.radio("Escolha a forma de normalização", 
                                         ["Não Alterar", "Entre 0 e 1", "Entre -1 e 1", "Desvio Padrão"], index=0)
            coluna_valor = st.selectbox("Selecione a coluna de valor para normalizar", df.columns)
            if tipo_normalizacao != "Não Alterar" and st.button("Aplicar Normalização"):
                df[coluna_valor] = normalizar(df[coluna_valor], tipo_normalizacao)
                st.session_state[f"df_preprocessed_{serie_selecionada}"] = df
                st.success("Normalização aplicada!")

        with tab4:
            st.subheader("Calcular Novas Colunas")
            calculo = st.radio("Escolha a nova coluna a calcular", 
                               ["Não Alterar", "Acumulado", "Variação Absoluta", "Variação Percentual", 
                                "Dia da Semana", "Número do Mês", "Ano com 4 Dígitos", "Ano com 2 Dígitos", 
                                "Contagem de Dias desde o Início", "Contagem de Dias desde o Início do Ano", 
                                "Contagem de Dias até o Fim do Ano"], index=0)
            if calculo != "Não Alterar" and st.button("Aplicar Cálculo de Nova Coluna"):
                df = calcular_novas_colunas(df, calculo, coluna_data)
                st.session_state[f"df_preprocessed_{serie_selecionada}"] = df
                st.success("Nova coluna calculada!")

        with tab5:
            st.subheader("Salvar, Baixar e Reverter Alterações")
            if st.button("Reverter para Dados Originais"):
                st.session_state[f"df_preprocessed_{serie_selecionada}"] = df_original.copy()
                st.success("Dados revertidos para o estado original.")

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Baixar Dataset Pré-processado", data=csv, file_name=f'dataset_pre_processado_{serie_selecionada}.csv', mime='text/csv')

            # Salvar configurações no log
            if "log" not in st.session_state:
                st.session_state.log = []
            if st.button("Salvar Configurações"):
                st.session_state.log.append(f"Configurações salvas para {serie_selecionada}")
                st.success(f"Configurações salvas para {serie_selecionada}")
                config_log = "\n".join(st.session_state.log)
                st.download_button(label="Baixar Configurações", data=config_log.encode(), file_name='configuracoes_projeto.txt', mime='text/plain')

    else:
        st.error("Nenhum dado foi carregado para pré-processamento.")
