import streamlit as st
import pandas as pd
from echarts_plots import grafico_barras, grafico_linhas

def analysis_page():
    st.title("Análise de Dados")

    if "df_original" in st.session_state and not st.session_state.df_original.empty:
        df = st.session_state.df_original.copy()

        # Garantir que o índice seja 'data' e esteja no formato datetime
        if df.index.name != 'data':
            df.set_index('data', inplace=True)
        
        # Converte o índice para datetime (caso ainda não esteja)
        try:
            df.index = pd.to_datetime(df.index, errors='coerce')
            if df.index.hasnans:
                st.warning("Algumas datas foram convertidas como NaT e serão removidas.")
                df = df.dropna(subset=[df.index.name])  # Remove linhas onde a data não pôde ser convertida
        except Exception as e:
            st.error(f"Erro ao converter índice para datetime: {e}")
            return

        # Filtrar colunas que possuem pelo menos um valor não nulo
        df = df.dropna(axis=1, how='all')

        # Formatar índice para 'dd/mm/aaaa' para exibição
        df_display = df.copy()
        df_display.index = df_display.index.strftime('%d/%m/%Y')

        # Exibir o DataFrame completo
        st.subheader("Dados das Séries Selecionadas")
        st.dataframe(df_display, use_container_width=True)

        # Iterar sobre cada coluna de valor
        for coluna in df.columns:
            # Verificar se a coluna possui algum valor não nulo
            if df[coluna].notna().any():
                st.divider()
                st.subheader(f"Análise da Coluna: `{coluna}`")

                # Criar três colunas (dados, estatística descritiva, gráfico)
                col1, col2, col3 = st.columns(3)

                # Coluna 1: Exibir os dados da série temporal
                with col1:
                    st.write("**Dados**")
                    df_coluna_display = df[[coluna]].copy()
                    df_coluna_display.index = df_coluna_display.index.strftime('%d/%m/%Y')
                    df_coluna_display.columns = ['Valor']
                    st.dataframe(df_coluna_display, use_container_width=True)

                # Coluna 2: Exibir estatísticas descritivas
                with col2:
                    st.write("**Estatísticas Descritivas**")
                    df_coluna_display.columns = ['Valor']
                    st.dataframe(df_coluna_display['Valor'].describe(), use_container_width=True)

                # Coluna 3: Gráfico com toggle para normalização
                with col3:
                    st.write("**Gráfico**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        # Chave única para cada coluna usando o nome da coluna
                        normalizar = st.toggle(f"Normalizar Dados", value=False, key=f"normalizar_{coluna}")
                        
                        df_plot = df[[coluna]].copy()
                        df_plot[coluna] = df_plot[coluna].fillna(0)

                        if normalizar:
                            min_val = df_plot[coluna].min()
                            max_val = df_plot[coluna].max()
                            if max_val > min_val:
                                df_plot[coluna] = (df_plot[coluna] - min_val) / (max_val - min_val)
                    
                    with col_b:
                        # Chave única para cada coluna usando o nome da coluna
                        tipo_grafico = st.selectbox("Escolha o tipo de gráfico", ['Linha', 'Barra'], key=f"grafico_{coluna}")

                    try:
                        if tipo_grafico == 'Linha':
                            grafico_linhas(df_plot, coluna)
                        elif tipo_grafico == 'Barra':
                            grafico_barras(df_plot, coluna)
                    except Exception as e:
                        st.error(f"Erro ao renderizar o gráfico: {e}")
            else:
                st.info(f"A coluna `{coluna}` não possui valores válidos para análise.")

    else:
        st.error("Nenhuma série foi carregada.")

