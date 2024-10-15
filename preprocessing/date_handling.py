import streamlit as st
import pandas as pd
import numpy as np
from echarts_plots import grafico_barras, grafico_linhas

# Função para aplicar o preenchimento nos valores nulos
def aplicar_preenchimento(df, metodos_preenchimento):
    for col, (metodo, valor_custom) in metodos_preenchimento.items():
        if metodo == "Último valor válido":
            df[col].ffill(inplace=True)
        elif metodo == "Próximo valor":
            df[col].bfill(inplace=True)
        elif metodo == "Média entre anterior e próximo":
            df[col].interpolate(method='linear', inplace=True)
        elif metodo == "Preencher com zero":
            df[col].fillna(0, inplace=True)
        elif metodo == "Valor personalizado" and valor_custom is not None:
            df[col].fillna(valor_custom, inplace=True)
    return df

# Função principal para manipulação de datas
def date_handling_page():
    st.title("Manipulação de Datas")

    if "df_original" in st.session_state and not st.session_state.df_original.empty:
        df = st.session_state.df_original.copy()

        # Escolher a frequência desejada
        st.subheader("Escolha a Frequência Desejada")
        frequencia = st.radio("Frequência", ["Diário", "Quinzenal", "Mensal", "Semestral", "Anual", "Personalizado (em dias)"], index=4)
        if frequencia == "Personalizado (em dias)":
            dias_personalizado = st.number_input("Informe o intervalo em dias", min_value=1, value=30, step=1)
        else:
            dias_personalizado = None

        # Aviso sobre a diminuição de frequência
        if frequencia != "Diário":
            st.warning("Diminuir a frequência (por exemplo, de anual para mensal) pode gerar distorções nos dados!")

        # Escolher método de preenchimento para cada coluna usando st.columns
        st.subheader("Método de Preenchimento dos valores nulos das Colunas")
        colunas = df.columns.tolist()
        colunas_st = st.columns(len(colunas))
        metodos_selecionados = {}

        for i, col in enumerate(colunas):
            with colunas_st[i]:
                st.markdown(f'`{col}`')
        colunas_st = st.columns(len(colunas))
        for i, col in enumerate(colunas):
            with colunas_st[i]:
                metodo = st.radio(
                    f"Método", 
                    ["Último valor", "Próximo valor", "Média anterior e próximo", 
                    "Preencher com zero", "Valor personalizado"], index=0, key=f"metodo_{col}")
                valor_custom = None
                if metodo == "Valor personalizado":
                    valor_custom = st.number_input(f"Valor personalizado para '{col}'", key=f"valor_custom_{col}")
                metodos_preenchimento = (metodo, valor_custom)
                metodos_selecionados[col] = metodos_preenchimento

                # Métricas de valores válidos
                valores_atuais = df[col].count()
                valores_originais = st.session_state.df_original[col].count()
                st.metric(label=f"Valores Válidos ({col})", value=int(valores_atuais), delta=int(valores_atuais - valores_originais), help=f"Valores originais: {valores_originais}")

        # Aplicar o preenchimento e remover valores nulos
        df = aplicar_preenchimento(df, metodos_preenchimento=metodos_selecionados)
        df.dropna(inplace=True)

        # Persistir o dataframe atualizado
        if df.empty:
            st.warning("O DataFrame ficou vazio após o preenchimento dos valores nulos. Por favor, revise os métodos selecionados.")
        else:
            st.session_state['df_atualizado'] = df

            # Determinar intervalo comum de datas
            data_minima_comum, data_maxima_comum = df.index.min(), df.index.max()
            if pd.isna(data_minima_comum) or pd.isna(data_maxima_comum):
                st.warning("Não foi possível determinar o intervalo comum de datas. Por favor, revise os métodos de preenchimento.")
            else:
                st.markdown(f"Data Mínima Comum: `{data_minima_comum.strftime('%d/%m/%Y')}`")
                st.markdown(f"Data Máxima Comum: `{data_maxima_comum.strftime('%d/%m/%Y')}`")
                st.markdown(f'Intervalo: `{(data_maxima_comum - data_minima_comum).days} dias`')

                # Slider para definir intervalo de datas
                st.subheader("Definir Intervalo de Datas")
                if not df.empty:
                    data_min = df.index.min().date()
                    data_max = df.index.max().date()

                    data_inicio, data_fim = st.slider(
                        "Selecione o intervalo de datas",
                        min_value=data_min,
                        max_value=data_max,
                        value=(data_min, data_max),
                        format="DD/MM/YYYY")

                    # Filtrar o DataFrame com base nas datas selecionadas
                    df_filtrado = df.loc[(df.index.date >= data_inicio) & (df.index.date <= data_fim)]

                    # Mostrar dados filtrados
                    if df_filtrado.empty:
                        st.warning("O DataFrame filtrado está vazio. Por favor, ajuste o intervalo de datas.")
                    else:
                        st.subheader("Dados Filtrados")
                        st.dataframe(df_filtrado)

                        # Visualização gráfica
                        st.subheader("Visualização Gráfica")
                        colunas_disponiveis = df_filtrado.columns.tolist()
                        colunas_selecionadas = st.multiselect("Selecione as séries para exibir no gráfico", colunas_disponiveis, default=colunas_disponiveis)

                        if colunas_selecionadas:
                            df_plot = df_filtrado[colunas_selecionadas]
                            if st.checkbox("Normalizar dados", value=False):
                                df_plot = (df_plot - df_plot.min()) / (df_plot.max() - df_plot.min())
                            grafico_linhas(df_plot, colunas=colunas_selecionadas, titulo="Gráfico de Linhas")

                        # Botão para aplicar as alterações
                        if st.button("Filtrar Dados", key="filtrar_dados"):
                            st.success("Dados filtrados conforme o intervalo selecionado!")

                        # Botão final para aplicar e substituir o dataframe original
                        if st.button("Aplicar Alterações", key="aplicar_alteracoes"):
                            st.session_state.df_original = df_filtrado
                            st.success("Alterações aplicadas ao DataFrame original!")

    else:
        st.error("Nenhum dado foi carregado para manipulação de datas.")

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    date_handling_page()
