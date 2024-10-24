import streamlit as st
import pandas as pd

# Função para inicializar ou restaurar o estado inicial
def reset_keys():
    # Verificar chaves associadas às colunas do dataframe
    for col in st.session_state['df_original'].columns:
        for chave in [
            f"referencia",
            f"normalizar_{col}",
            f"usar_serie_{col}",
            f"enviar_{col}",
            f"preenchimento_{col}",
            f"normalizar_{col}",
            f"selecionar_{col}",
            f"toggle_{col}",  # Adicionando chave de toggle
        ]:
            if chave in st.session_state:
                del st.session_state[chave]

    # Verificar chaves associadas ao slider e datas comuns
    for chave in [
        "slider_min",
        "slider_max",
        "slider_valor_min",
        "slider_valor_max",
        "data_minima_comum",
        "data_maxima_comum",
    ]:
        if chave in st.session_state:
            del st.session_state[chave]


def nomes_series():
    cols = st.columns([1] + [1] * len(st.session_state['df_original'].columns.tolist()))
    cols[0].markdown(f"###### Nome da Série")
    for i, col in enumerate(st.session_state['df_original'].columns.tolist()):
        cols[i + 1].markdown(f"##### {col}")

def selecionar():
    cols = st.columns([1] + [1] * len(st.session_state['df_original'].columns.tolist()))
    cols[0].markdown(f"###### Usar série no envio")
    for i, col in enumerate(st.session_state['df_original'].columns.tolist()):
        cols[i + 1].checkbox(f"", value=st.session_state[f"enviar_{col}"], key=f"enviar_{col}")

def resumo():
    with st.expander('Resumo da compatibilização de datas'):
        # Sexta linha: Data mínima e máxima do df_original para cada série
        cols = st.columns([1] + [1] * len(st.session_state['df_original'].columns.tolist()))
        cols[0].markdown(f"###### Data mínima original")
        for i, col in enumerate(st.session_state['df_original'].columns.tolist()):
            data_min_original = st.session_state['df_original'][col].dropna().index.min()
            cols[i + 1].write(data_min_original.strftime('%d/%m/%Y') if data_min_original else 'N/A')
        cols = st.columns([1] + [1] * len(st.session_state['df_original'].columns.tolist()))
        cols[0].markdown(f"###### Data máxima original")
        for i, col in enumerate(st.session_state['df_original'].columns.tolist()):
            data_max_original = st.session_state['df_original'][col].dropna().index.max()
            cols[i + 1].write(data_max_original.strftime('%d/%m/%Y') if data_max_original else 'N/A')
        # Quarta linha: Valores válidos filtrados
        cols = st.columns([1] + [1] * len(st.session_state['df_original'].columns.tolist()))
        cols[0].markdown(f"###### Valores válidos nas datas comuns/totais")
        for i, col in enumerate(st.session_state['df_original'].columns.tolist()):
            valores_filtrados = st.session_state['df_original'][col].loc[st.session_state["slider_valor_min"]:st.session_state["slider_valor_max"]].reindex(st.session_state['df_original'][st.session_state["referencia"]].dropna().index).count()
            valores_originais = st.session_state['df_original'][col].count()
            cols[i + 1].markdown(f'`{valores_filtrados}`/`{valores_originais}`')
        cols = st.columns([1] + [1] * len(st.session_state['df_original'].columns.tolist()))
        cols[0].markdown(f"###### Valores nulos nas datas comuns")
        for i, col in enumerate(st.session_state['df_original'].columns.tolist()):
            valores_nulos_filtrados = len(st.session_state['df_original'][st.session_state["referencia"]].loc[st.session_state["slider_valor_min"]:st.session_state["slider_valor_max"]].dropna().index) - st.session_state['df_original'][col].loc[st.session_state["slider_valor_min"]:st.session_state["slider_valor_max"]].reindex(st.session_state['df_original'][st.session_state["referencia"]].dropna().index).count()
            if valores_nulos_filtrados == 0:
                cols[i + 1].success(valores_nulos_filtrados)
            else:
                cols[i + 1].warning(valores_nulos_filtrados)

def slider():
    # **Aqui está o expander do slider imediatamente acima do gráfico**
    st.session_state["slider_valor_min"], st.session_state["slider_valor_max"] = st.slider("Selecione o intervalo de datas", min_value=st.session_state["slider_min"], max_value=st.session_state["slider_max"], value=(st.session_state["slider_valor_min"], st.session_state["slider_valor_max"]), format="DD/MM/YYYY")


