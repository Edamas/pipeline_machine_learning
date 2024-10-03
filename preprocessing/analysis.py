import streamlit as st
import pandas as pd

def analysis_page():
    st.title("Análise de Dados")

    if "df_original" in st.session_state and not st.session_state.df_original.empty:
        df = st.session_state.df_original.copy()

        # Garantir que o índice seja 'data' e esteja no formato datetime
        if df.index.name != 'data':
            df.set_index('data', inplace=True)
        
        df.index = pd.to_datetime(df.index)

        # Criar uma cópia para exibição, formatando o índice como 'dd/mm/aaaa'
        df_display = df.copy()
        df_display.index = df_display.index.strftime('%d/%m/%Y')

        # Exibir o DataFrame completo com container_width
        st.subheader("Dados das Séries Selecionadas")
        st.dataframe(df_display, use_container_width=True)

        # Iterar sobre cada coluna de valor
        for coluna in df.columns:
            # Adicionar um divisor para separar as análises das colunas
            st.divider()

            # Subheader com o nome da coluna
            st.subheader(f"Análise da Coluna: {coluna}")

            # Criar três colunas (dados, estatística descritiva, gráfico)
            col1, col2, col3 = st.columns(3)

            # Coluna 1: Exibir os dados da time series para a coluna atual
            with col1:
                st.write("**Dados**")
                st.dataframe(df[[coluna]].copy(), use_container_width=True)

            # Coluna 2: Exibir estatísticas descritivas para a coluna atual
            with col2:
                st.write("**Estatísticas Descritivas**")
                st.dataframe(df[coluna].describe(), use_container_width=True)

            # Coluna 3: Exibir gráfico para a coluna atual com toggle para normalização
            with col3:
                st.write("**Gráfico**")

                # Toggle para normalizar os dados
                normalizar = st.toggle(f"Normalizar Dados ({coluna})", value=False)

                df_plot = df[[coluna]].copy()

                if normalizar:
                    # Normalizar os dados
                    df_plot[coluna] = (df_plot[coluna] - df_plot[coluna].min()) / (df_plot[coluna].max() - df_plot[coluna].min())

                # Exibir o gráfico de linha
                st.line_chart(df_plot)

    else:
        st.error("Nenhuma série foi carregada.")
