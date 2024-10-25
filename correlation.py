# correlation.py

import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations
from datetime import datetime, timedelta

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy import stats
import statsmodels.api as sm

from echarts_plots import line_chart, scatter_plot_with_regression, scatter_3d_plot

def criar_dataframe_selecionavel(df, titulo, descricao, df_key, col=None, hide_index=False):
    titulo = f"**{titulo}**: {descricao}"
    if col:
        col.write(titulo)
        event = col.dataframe(df, use_container_width=True, hide_index=hide_index, on_select="rerun", selection_mode="single-row")
    else:
        st.write(titulo)
        event = st.dataframe(df, use_container_width=True, hide_index=hide_index, on_select="rerun", selection_mode="single-row")
    
    # Armazena o número de registros filtrados
    st.session_state[f'{df_key}_filtrado'] = len(df)
    if 'selection' in event:
        if 'rows' in event['selection']:
            if event['selection']['rows']:
                return event['selection']["rows"]
    return []

def correlation_page():
    st.title("Análise Estatística e de Correlação")

    if "df_original" in st.session_state and not st.session_state.df_original.empty:
        df = st.session_state['df_original']  # Use the DataFrame directly from session state

        # Ensure that the index is datetime
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            st.error("O índice do DataFrame não é do tipo datetime.")
            return

        # Exclude non-numeric columns for certain operations
        numerical_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        # Tabs
        tab1, tab_series, tab2, tab3 = st.tabs(["Análise Geral", "Análise de Séries Individuais", "Análise Bivariada 2D", "Análise Trivariada 3D"])

        # --------------------- Tab 1: Análise Geral ---------------------
        with tab1:
            st.header("Análise Geral do DataFrame")

            # Advanced Line Chart
            with st.expander("Gráfico de Linhas", True):
                # Add normalization option
                normalize_data = st.checkbox("Normalizar dados para exibição nos gráficos", value=False)
                for col in numerical_columns:
                    line_chart(
                        dataframe=(
                            (df[numerical_columns] - df[numerical_columns].min()) / (df[numerical_columns].max() - df[numerical_columns].min())) if normalize_data else df,
                        coluna=col,
                        #normalize=normalize_data,
                        titulo=col,
                        key=f"grafico_linha_{col}"
                        )

            # Correlation Matrix
            with st.expander("Matriz de Correlação", True):
                corr_matrix = df[numerical_columns].corr()
                st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm').format("{:.4f}"), use_container_width=True)

            # Statistical Summary
            with st.expander("Sumário Estatístico", True):
                summary_df = df[numerical_columns].describe().transpose()
                st.dataframe(summary_df, use_container_width=True)

            # Show the original DataFrame
            with st.expander("Ver DataFrame Original", expanded=True):
                st.dataframe(df, use_container_width=True)

        # --------------------- Tab Series: Análise de Séries Individuais ---------------------
        with tab_series:
            st.header("Análise de Séries Individuais")

            # DataFrame of series
            series_names = [col for col in numerical_columns if col not in ['date', 'Date', 'index']]
            series_df = pd.DataFrame(series_names, columns=['Série'])
            selected_indices = criar_dataframe_selecionavel(
                series_df,
                titulo="Selecione uma Série para Análise",
                descricao="Clique em uma linha para selecionar a série desejada.",
                df_key="dataframe_tab_series",
                hide_index=True
            )

            if selected_indices:
                selected_series_name = series_df.iloc[selected_indices[0]]['Série']
                st.write(f"**Série Selecionada:** {selected_series_name}")

                # Proceed with analysis and plotting
                df_series = df[[selected_series_name]].dropna()
                if not df_series.empty:
                    x = df_series.index  # Use index as date
                    y = df_series[selected_series_name]
                    # Add normalization option
                    normalize_data2 = st.checkbox("Normalizar dados para exibição", key=f'norm_{selected_series_name}', value=False)
                    line_chart(
                        dataframe=(
                            (df_series[selected_series_name] - df_series[selected_series_name].min()) / (df_series[selected_series_name].max() - df_series[selected_series_name].min())) if normalize_data else df_series,
                        coluna=selected_series_name,
                        #normalize=normalize_data,
                        titulo=selected_series_name,
                        key=f"grafico_linha2_{selected_series_name}"
                        )

                    # Place statistical summary and OLS statistics at the end
                    col_summary = st.container()

                    # Statistical Summary
                    with col_summary:
                        st.subheader("Sumário Estatístico")
                        stats_series = df[selected_series_name].describe()
                        st.dataframe(stats_series.to_frame(), use_container_width=True)
                else:
                    st.warning("Os dados selecionados não contêm valores suficientes para análise.")

            else:
                st.info("Selecione uma série na tabela acima para ver a análise detalhada.")

        # --------------------- Tab 2: Análise Bivariada 2D ---------------------
        with tab2:
            st.header("Análise Detalhada entre Pares de Séries")

            # Compute detailed analysis between pairs of series
            analysis_data = []

            for col1, col2 in combinations(numerical_columns, 2):
                x = df[col1].values
                y = df[col2].values

                # Remove NaN values
                mask = ~np.isnan(x) & ~np.isnan(y)
                x = x[mask]
                y = y[mask]

                if len(x) < 2:
                    continue  # Skip if not enough data

                correlation = np.corrcoef(x, y)[0, 1]
                analysis_data.append({
                    'Série X': col1,
                    'Série Y': col2,
                    'Correlação (R)': correlation,
                })

            if analysis_data:
                analysis_df = pd.DataFrame(analysis_data)
                # Sort the DataFrame by correlation in descending order
                analysis_df_sorted = analysis_df.sort_values(by='Correlação (R)', ascending=False)
                # Reset index to have a default integer index
                analysis_df_sorted = analysis_df_sorted.reset_index(drop=True)

                # Create selectable DataFrame
                selected_indices = criar_dataframe_selecionavel(
                    analysis_df_sorted,
                    titulo="Selecione um Par de Séries para Análise",
                    descricao="Clique em uma linha para selecionar o par de séries desejado.",
                    df_key="dataframe_tab2",
                    hide_index=True
                )

                if selected_indices:
                    selected_pair = analysis_df_sorted.iloc[selected_indices[0]]
                    coluna_x = selected_pair['Série X']
                    coluna_y = selected_pair['Série Y']

                    st.write(f"**Série X:** {coluna_x}")
                    st.write(f"**Série Y:** {coluna_y}")

                    # Proceed with analysis and plotting
                    df_corr = df[[coluna_x, coluna_y]].dropna()
                    if not df_corr.empty:
                        # Plot
                        scatter_plot_with_regression(
                            dataframe=df_corr,
                            x_column=coluna_x,
                            y_column=coluna_y,
                            normalize=normalize_data,
                            title=f"Correlação entre {coluna_x} e {coluna_y}",
                            key=f"scatter_plot_{coluna_x}_{coluna_y}"
                        )
                    else:
                        st.warning("Os dados selecionados não contêm valores suficientes para análise.")
                else:
                    st.info("Selecione um par de séries na tabela acima para ver a análise detalhada.")
            else:
                st.warning("Não há dados suficientes para análise bivariada.")

        # --------------------- Tab 3: Análise Trivariada 3D ---------------------
        tab3 = st.tabs(["Análise Detalhada entre Trios de Séries"])[0]
        with tab3:
            st.header("Análise Detalhada entre Trios de Séries")

            numerical_columns = df.select_dtypes(include=[np.number]).columns.tolist()

            # Computar combinações de três séries
            analysis_data = []

            for col1, col2, col3 in combinations(numerical_columns, 3):
                x1 = df[col1].values
                x2 = df[col2].values
                y = df[col3].values

                # Remover valores NaN
                mask = ~np.isnan(x1) & ~np.isnan(x2) & ~np.isnan(y)
                x1 = x1[mask]
                x2 = x2[mask]
                y = y[mask]

                if len(x1) < 3:
                    continue  # Pular se não houver dados suficientes

                # Calcular soma das correlações
                correlation = np.corrcoef(x1, y)[0, 1] + np.corrcoef(x2, y)[0, 1]
                analysis_data.append({
                    'Série X1': col1,
                    'Série X2': col2,
                    'Série Y': col3,
                    'Correlação Total': correlation,
                })

            if analysis_data:
                analysis_df = pd.DataFrame(analysis_data)
                # Ordenar pelo total de correlação em ordem decrescente
                analysis_df_sorted = analysis_df.sort_values(by='Correlação Total', ascending=False).reset_index(drop=True)

                # Criar uma tabela interativa para seleção
                selected_indices = criar_dataframe_selecionavel(
                    analysis_df_sorted,
                    titulo="Selecione um Trio de Séries para Análise",
                    descricao="Selecione o índice do trio de séries desejado.",
                    df_key="dataframe_tab3",
                    hide_index=True
                )

                if selected_indices:
                    selected_trio = analysis_df_sorted.iloc[selected_indices[0]]
                    coluna_x1 = selected_trio['Série X1']
                    coluna_x2 = selected_trio['Série X2']
                    coluna_y = selected_trio['Série Y']

                    st.write(f"**Série X1:** {coluna_x1}")
                    st.write(f"**Série X2:** {coluna_x2}")
                    st.write(f"**Série Y:** {coluna_y}")

                    # Proceed with analysis and 3D plotting
                    data = df[[coluna_x1, coluna_x2, coluna_y]].dropna()

                    if not data.empty:
                        # Plot
                        scatter_3d_plot(
                            dataframe=data,
                            x_column=coluna_x1,
                            y_column=coluna_x2,
                            z_column=coluna_y,
                            normalize=normalize_data,
                            title=f"Relação entre {coluna_x1}, {coluna_x2} e {coluna_y}",
                            key=f"scatter_3d_{coluna_x1}_{coluna_x2}_{coluna_y}"
                        )
                    else:
                        st.warning("Os dados selecionados não contêm valores suficientes para análise.")
                else:
                    st.info("Selecione um trio de séries na tabela acima para ver a análise detalhada.")
            else:
                st.warning("Não há dados suficientes para análise trivariada.")

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    correlation_page()
