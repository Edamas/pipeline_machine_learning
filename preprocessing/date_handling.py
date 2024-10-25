import streamlit as st
import pandas as pd
from echarts_plots import grafico_linhas
from preprocessing.funcoes_date_handling import *

def get_min_max():
    min_dates = st.session_state['df_original'].apply(lambda col: col.dropna().index.min())
    max_dates = st.session_state['df_original'].apply(lambda col: col.dropna().index.max())
    data_min_comum = min_dates.max()
    data_max_comum = max_dates.min()
    return data_min_comum, data_max_comum

# Função para inicializar ou restaurar o estado inicial
def inicializar_estado():
    data_min_comum, data_max_comum = get_min_max()
    if data_min_comum is None or data_max_comum is None:
        st.error("Verifique se as séries possuem um intervalo de datas comum.")

    chaves_gerais = {
        "slider_min": st.session_state['df_original'].index.min().date(),
        "slider_max": st.session_state['df_original'].index.max().date(),
        "data_minima_comum": data_min_comum,
        "data_maxima_comum": data_max_comum,
    }
    for chave, valor_padrao in chaves_gerais.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor_padrao

    if "slider_valor_min" not in st.session_state:
        st.session_state["slider_valor_min"] = data_min_comum.date()
    if "slider_valor_max" not in st.session_state:
        st.session_state["slider_valor_max"] = data_max_comum.date()

    if 'df_temp' not in st.session_state:
        st.session_state['df_temp'] = st.session_state['df_original'].copy()

    referencia_default = st.session_state['df_original'].loc[data_min_comum:data_max_comum].count().idxmin()

    for col in st.session_state.df_original.columns:
        chaves_coluna = {
            "referencia": referencia_default,
            f"normalizar_{col}": False,
            f"usar_serie_{col}": True,
            f"enviar_{col}": True,
            f"preenchimento_{col}": "Último valor válido",
            f"selecionar_{col}": True,
        }
        for chave, valor_padrao in chaves_coluna.items():
            if chave not in st.session_state:
                st.session_state[chave] = valor_padrao

def reset_keys():
    # Função para resetar as chaves no session_state
    chaves_para_resetar = [
        "slider_min", "slider_max", "slider_valor_min", "slider_valor_max",
        "data_minima_comum", "data_maxima_comum", "df_temp",
    ]
    for chave in chaves_para_resetar:
        if chave in st.session_state:
            del st.session_state[chave]
    # Remover chaves específicas de colunas
    for col in st.session_state.df_original.columns:
        chaves = [
            f"referencia", f"normalizar_{col}", f"usar_serie_{col}", f"enviar_{col}",
            f"preenchimento_{col}", f"selecionar_{col}",
        ]
        for chave in chaves:
            if chave in st.session_state:
                del st.session_state[chave]

def botoes():
    cols = st.columns(3)
    with cols[0]:
        if st.button("Ajustar datas para intervalo comum"):
            st.session_state["slider_valor_min"] = st.session_state["data_minima_comum"].date()
            st.session_state["slider_valor_max"] = st.session_state["data_maxima_comum"].date()
            atualizar_df_temp()
            st.rerun()
    with cols[1]:
        if st.button("Restaurar para séries originais (resetar)"):
            reset_keys()
            inicializar_estado() 
            st.rerun()
    with cols[2]:
        if st.button("Aplicar e enviar alterações"):
            st.session_state['df_original'] = st.session_state['df_temp'].copy()
            st.success("Alterações enviadas!")
            st.rerun()

# Função para atualizar o df_temp no session_state com base no slider
def atualizar_df_temp():
    referencia = st.session_state['referencia']
    data_min = pd.to_datetime(st.session_state["date_slider"][0])
    data_max = pd.to_datetime(st.session_state["date_slider"][1])

    df_filtrado = st.session_state["df_original"].copy()
    df_filtrado.index = pd.to_datetime(df_filtrado.index)
    df_filtrado = df_filtrado.sort_index(ascending=True)
    df_filtrado = df_filtrado.loc[data_min:data_max]

    if df_filtrado.empty:
        st.warning("O intervalo selecionado não contém dados.")
        st.session_state["df_temp"] = pd.DataFrame()
        return

    colunas = df_filtrado.columns
    colunas_para_exibir = [col for col in colunas if st.session_state.get(f"usar_serie_{col}", True)]

    indices_coluna = df_filtrado[referencia].dropna().index

    df_temp = pd.DataFrame(index=indices_coluna)

    for col in colunas_para_exibir:
        metodo = st.session_state.get(f"preenchimento_{col}", "Último valor válido")
        coluna = df_filtrado[col]
        df_col_temp = coluna.reindex(indices_coluna).copy()

        if col != referencia:
            for idx in indices_coluna:
                if pd.isna(df_col_temp.loc[idx]):
                    if metodo == "Último valor válido":
                        df_col_temp.loc[idx] = df_col_temp.loc[:idx].ffill().iloc[-1]
                    elif metodo == "Próximo valor":
                        df_col_temp.loc[idx] = df_col_temp.loc[idx:].bfill().iloc[0]
                    elif metodo == "Média entre anterior e próximo":
                        prev_val = df_col_temp.loc[:idx].ffill().iloc[-1]
                        next_val = df_col_temp.loc[idx:].bfill().iloc[0]
                        df_col_temp.loc[idx] = (prev_val + next_val) / 2
                    elif metodo == "Preencher com zero":
                        df_col_temp.loc[idx] = 0
        else:
            df_col_temp = df_col_temp.dropna()
        df_temp[col] = df_col_temp

    for col in colunas_para_exibir:
        if st.session_state.get(f"normalizar_{col}", False):
            min_val = df_temp[col].min()
            max_val = df_temp[col].max()
            if max_val != min_val:
                df_temp[col] = (df_temp[col] - min_val) / (max_val - min_val)

    st.session_state["df_temp"] = df_temp


def nomes_series():
    cols_list = st.session_state['df_original'].columns.tolist()
    cols = st.columns([1] + [1] * len(cols_list))
    cols[0].markdown(f"**Séries**")
    for i, col in enumerate(cols_list):
        cols[i + 1].markdown(f"**{col}**")

def checkbox_referencia():
    cols_list = st.session_state['df_original'].columns.tolist()
    cols = st.columns([1] + [1] * len(cols_list))
    cols[0].markdown(f"###### Usar datas desta série como datas de referência")

    # Captura a referência atual ou define um padrão
    data_min_comum, data_max_comum = get_min_max()
    referencia_default = st.session_state['df_original'].loc[data_min_comum:data_max_comum].count().idxmin()

    # Inicializa o estado dos checkboxes no session_state
    for col in cols_list:
        checkbox_key = f"toggle_{col}"
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = (col == st.session_state.get("referencia", referencia_default))

    # Função chamada quando uma checkbox é alterada
    def checkbox_changed(selected_col):
        for col_inner in cols_list:
            checkbox_key_inner = f"toggle_{col_inner}"
            if col_inner != selected_col:
                st.session_state[checkbox_key_inner] = False
        # Atualiza a referência se tiver mudado
        if st.session_state.get("referencia") != selected_col:
            st.session_state["referencia"] = selected_col
            atualizar_df_temp()

    # Renderiza os checkboxes com o callback on_change
    for i, col in enumerate(cols_list):
        checkbox_key = f"toggle_{col}"
        cols[i + 1].checkbox(
            "Referência",
            value=st.session_state[checkbox_key],
            key=checkbox_key,
            on_change=checkbox_changed,
            args=(col,),
            label_visibility='collapsed'  # Para evitar avisos sobre labels vazios
        )

def preencher_valores_nulos():
    # Terceira linha: Preenchimento de valores nulos
    cols = st.columns([1] + [1] * len(st.session_state['df_original'].columns.tolist()))
    exibiu_titulo = False
    for i, col in enumerate(st.session_state['df_original'].columns.tolist()):
        valores_nulos_filtrados = len(st.session_state['df_original'][st.session_state["referencia"]].loc[st.session_state["slider_valor_min"]:st.session_state["slider_valor_max"]].dropna().index) - st.session_state['df_original'][col].loc[st.session_state["slider_valor_min"]:st.session_state["slider_valor_max"]].reindex(st.session_state['df_original'][st.session_state["referencia"]].dropna().index).count()

        if valores_nulos_filtrados != 0:
            if not exibiu_titulo:
                cols[0].markdown(f"###### Preenchimento de valores nulos")
                exibiu_titulo = True
            cols[i + 1].radio(f"", ["Último valor válido", "Próximo valor", "Média entre anterior e próximo", "Preencher com zero"], key=f"preenchimento_{col}", label_visibility='collapsed')

def normalizar():
    cols_list = st.session_state['df_original'].columns.tolist()
    # Criar colunas para o layout
    cols = st.columns([1] + [1] * len(cols_list))
    cols[0].markdown(f"###### Normalizar dados para envio")
    
    # Inicializa o estado dos checkboxes no session_state apenas se ainda não estiver definido
    for col in cols_list:
        checkbox_key = f"normalizar_{col}"
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = False

    # Função chamada quando uma checkbox é alterada
    def checkbox_changed():
        atualizar_df_temp()

    # Renderiza as checkboxes sem modificar o session_state durante a renderização
    for i, col in enumerate(cols_list):
        checkbox_key = f"normalizar_{col}"
        cols[i + 1].checkbox(
            "",
            value=st.session_state[checkbox_key],
            key=checkbox_key,
            on_change=checkbox_changed,
            label_visibility='collapsed'  # Para evitar avisos
        )

def selecionar():
    cols_list = st.session_state['df_original'].columns.tolist()
    # Criar colunas para o layout
    cols = st.columns([1] + [1] * len(cols_list))
    cols[0].markdown(f"###### Usar série no envio")
    
    # Inicializa o estado dos checkboxes no session_state apenas se ainda não estiver definido
    for col in cols_list:
        checkbox_key = f"usar_serie_{col}"
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = True

    # Função chamada quando uma checkbox é alterada
    def checkbox_changed():
        atualizar_df_temp()

    # Renderiza as checkboxes sem modificar o session_state durante a renderização
    for i, col in enumerate(cols_list):
        checkbox_key = f"usar_serie_{col}"
        cols[i + 1].checkbox(
            "",
            value=st.session_state[checkbox_key],
            key=checkbox_key,
            on_change=checkbox_changed,
            label_visibility='collapsed'  # Para evitar avisos
        )

def resumo():
    colunas = st.session_state['df_temp'].columns.to_list()
    with st.expander('Resumo da compatibilização de datas', expanded=False):
        # Data mínima original
        cols = st.columns([1] + [1] * len(colunas))
        cols[0].markdown(f"###### Data mínima original")
        for i, col in enumerate(colunas):
            data_min_original = st.session_state['df_original'][col].dropna().index.min()
            cols[i + 1].write(data_min_original.strftime('%d/%m/%Y') if data_min_original else 'N/A')
        
        # Data mínima filtrada
        cols = st.columns([1] + [1] * len(colunas))
        cols[0].markdown(f"###### Data mínima filtrada")
        for i, col in enumerate(colunas):
            data_min_filtrada = st.session_state['df_temp'][col].dropna().index.min()
            cols[i + 1].write(data_min_filtrada.strftime('%d/%m/%Y') if data_min_filtrada else 'N/A')

        # Intervalo de dias
        cols = st.columns([1] + [1] * len(colunas))
        cols[0].markdown(f"###### Intervalo de dias")
        for i, col in enumerate(colunas):
            data_min = st.session_state['df_temp'][col].dropna().index.min()
            data_max = st.session_state['df_temp'][col].dropna().index.max()
            if data_min and data_max:
                intervalo_filtrado_dias = (data_max - data_min).days
                cols[i + 1].write(f"{intervalo_filtrado_dias} dias")
            else:
                cols[i + 1].write("N/A")

        # Data máxima filtrada
        cols = st.columns([1] + [1] * len(colunas))
        cols[0].markdown(f"###### Data máxima filtrada")
        for i, col in enumerate(colunas):
            data_max_filtrada = st.session_state['df_temp'][col].dropna().index.max()
            cols[i + 1].write(data_max_filtrada.strftime('%d/%m/%Y') if data_max_filtrada else 'N/A')

        # Data máxima original
        cols = st.columns([1] + [1] * len(colunas))
        cols[0].markdown(f"###### Data máxima original")
        for i, col in enumerate(colunas):
            data_max_original = st.session_state['df_original'][col].dropna().index.max()
            cols[i + 1].write(data_max_original.strftime('%d/%m/%Y') if data_max_original else 'N/A')
        
        # Valores válidos nas datas comuns/totais
        cols = st.columns([1] + [1] * len(colunas))
        cols[0].markdown(f"###### Valores válidos nas datas comuns/totais")
        for i, col in enumerate(colunas):
            valores_originais = st.session_state['df_original'][col].dropna().shape[0]
            valores_filtrados = st.session_state['df_temp'][col].dropna().shape[0]
            cols[i + 1].markdown(f'`{valores_filtrados}`/`{valores_originais}`')

        # Valores nulos nas datas comuns
        cols = st.columns([1] + [1] * len(colunas))
        cols[0].markdown(f"###### Valores nulos nas datas comuns")
        for i, col in enumerate(colunas):
            total_datas = st.session_state['df_temp'].shape[0]
            valores_validos = st.session_state['df_temp'][col].dropna().shape[0]
            valores_nulos = total_datas - valores_validos
            if valores_nulos == 0:
                cols[i + 1].success(valores_nulos)
            else:
                cols[i + 1].warning(valores_nulos)

def slider():
    # Função para renderizar o slider de seleção de datas
    data_min = st.session_state["slider_min"]
    data_max = st.session_state["slider_max"]

    # Converter para datetime.date se necessário
    if isinstance(data_min, pd.Timestamp):
        data_min = data_min.date()
    if isinstance(data_max, pd.Timestamp):
        data_max = data_max.date()

    slider_key = "date_slider"

    # Renderizar o slider com on_change
    st.slider(
        "Selecione o intervalo de datas:",
        min_value=data_min,
        max_value=data_max,
        value=(st.session_state["slider_valor_min"], st.session_state["slider_valor_max"]),
        key=slider_key,
        on_change=atualizar_df_temp,
    )


def date_handling_page():
    st.title("Manipulação de Datas")
    
    if "df_original"  in st.session_state:
        if not st.session_state.df_original.empty:
            inicializar_estado()
            nomes_series()
            checkbox_referencia()
            preencher_valores_nulos()
            normalizar()
            selecionar()
            resumo()
            botoes()
            slider()
            grafico_linhas(
                st.session_state["df_temp"],
                [col for col in st.session_state['df_temp'].columns.tolist() if st.session_state.get(f"usar_serie_{col}", True)],
                titulo="Gráfico de Linhas"
            )
            st.dataframe(st.session_state["df_temp"], use_container_width=True)
        else:
            st.error("Nenhum dado foi carregado para manipulação de datas.")
    else:
        st.error("Nenhum dado foi carregado para manipulação de datas.")

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    date_handling_page()
