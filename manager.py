import pandas as pd
import streamlit as st
from streamlit import session_state as ss
import numpy as np

def cast_dtype_explicitly(serie, para_float=False):
    """
    Converte a Series para um tipo de dado compatível.
    
    Parâmetros:
    - serie (pd.Series): A série a ser convertida.
    - para_float (bool): Se True, converte a série para float, independentemente do tipo original.
    
    Retorna:
    - pd.Series: A série com o dtype apropriado.
    """
    if pd.api.types.is_float_dtype(serie) or pd.api.types.is_integer_dtype(serie):
        return serie.astype(float) if pd.api.types.is_integer_dtype(serie) else serie
    else:
        raise TypeError(f"Tipo de dado não suportado: {serie.dtype}")

def nulos(serie, data_min, data_max, metodo):
    if metodo == 'Zeros':
        serie.loc[data_min:data_max] = serie.loc[data_min:data_max].fillna(0)
    elif metodo == 'Média':
        media = serie.loc[data_min:data_max].mean()
        serie.loc[data_min:data_max] = serie.loc[data_min:data_max].fillna(media)
    elif metodo == 'Último valor válido':
        serie.loc[data_min:data_max] = serie.loc[data_min:data_max].ffill()
    elif metodo == 'Próximo valor válido':
        serie.loc[data_min:data_max] = serie.loc[data_min:data_max].bfill()
    else:
        st.warning('O método de preenchimento de valores nulos não reconhecido. Preenchendo nulos com zeros.')
        serie.loc[data_min:data_max] = serie.loc[data_min:data_max].fillna(0)
    return serie

def normalizacao(serie, data_min, data_max, normalizar):
    valores = serie.loc[data_min:data_max]
    if normalizar:
        serie = serie.astype(np.float64).copy()
        serie.loc[data_min:data_max] = (valores - min(valores)) / (max(valores) - min(valores))
    return serie

def configuracoes_iniciais():
    ss['configuracoes'] = pd.DataFrame(columns=['funcao', 'nome', 'data_min', 'data_max', 'normalizar', 'preencher_nulos', 'media', 'visualizacao'])

def series_manager():
    st.markdown("### 📈 Gerenciamento de Séries Temporais")
    botoes()

    # Inicializa o dicionário de ação na primeira execução
    if 'ação' not in ss or not isinstance(ss['ação'], dict):
        ss['ação'] = {"recalcular": True, "comuns": False, "modificado": False}

    # Copia o dataframe original, eliminando linhas totalmente nulas
    df_original = ss['df_original'].dropna(how='all').copy()
    datas_min = [df_original[col].dropna().index.min() for col in df_original.columns if not df_original[col].dropna().empty]
    datas_max = [df_original[col].dropna().index.max() for col in df_original.columns if not df_original[col].dropna().empty]
    data_min_comum = max(datas_min) if datas_min else None
    data_max_comum = min(datas_max) if datas_max else None

    # Verifica e ajusta datas dependendo do estado do toggle e do dicionário de ação
    if ss['ação']["modificado"]:
        if ss['ação']["comuns"]:
            # Ajusta todas as datas para o intervalo comum
            ss['configuracoes']['data_min'] = data_min_comum
            ss['configuracoes']['data_max'] = data_max_comum
        else:
            # Ajusta as datas individualmente para cada série
            for nome in df_original.columns:
                if nome in ss['configuracoes']['nome'].values:
                    # Define as datas mínimas e máximas específicas para cada série
                    data_min = ss['df_original'][nome].dropna().index.min()
                    data_max = ss['df_original'][nome].dropna().index.max()
                    ss['configuracoes'].loc[ss['configuracoes']['nome'] == nome, 'data_min'] = data_min
                    ss['configuracoes'].loc[ss['configuracoes']['nome'] == nome, 'data_max'] = data_max

        ss['ação']["modificado"] = False

    config_list = []
    df_editado = df_original.copy()

    for idx, nome in enumerate(df_original.columns):
        serie = df_original[nome].copy()
        
        # Ajusta as configurações de cada série
        if 'nome' not in ss['configuracoes'].columns or nome not in ss['configuracoes']['nome'].values:
            config = {
                'funcao': 'X', 'nome': nome, 'normalizar': False, 'preencher_nulos': 'Último valor válido',
                'data_min': ss['df_original'][nome].index.min(), 'data_max': ss['df_original'][nome].index.max()
            }
        else:
            config = ss['configuracoes'].loc[ss['configuracoes']['nome'] == nome].iloc[0].to_dict()

        # Define as datas ajustadas conforme estado do toggle e limites
        data_min_input = config.get('data_min', ss['df_original'][nome].index.min())
        data_max_input = config.get('data_max', ss['df_original'][nome].index.max())
        
        # Ajusta datas com base no estado do toggle
        if ss['ação']["comuns"]:
            data_min = max(data_min_comum, data_min_input)
            data_max = min(data_max_comum, data_max_input)
        else:
            data_min = max(ss['df_original'][nome].index.min(), data_min_input)
            data_max = min(ss['df_original'][nome].index.max(), data_max_input)

        # Aplica os dtype, preenchimentos de nulos e normalizações
        
        serie = cast_dtype_explicitly(serie)
        serie = nulos(serie, data_min, data_max, metodo=config['preencher_nulos'])
        serie = normalizacao(serie, data_min, data_max, normalizar=config['normalizar'])
        

        # Calcula a média e atualiza as configurações
        media = serie.loc[data_min:data_max].mean()
        config['media'] = media
        config['visualizacao'] = normalizacao(serie[data_min:data_max], data_min, data_max, True).fillna(0).tolist()
        config['data_min'] = data_min
        config['data_max'] = data_max
        config_list.append(config)

        # Atualiza o df_editado para garantir que não tenha valores nulos
        # Converte a coluna para float, pois float aceita valores nulos (NaN)
        #df_editado.loc[:, nome] = df_editado[nome].astype('float64')  # Converte para float64 para aceitar valores nulos e garantir precisão
        #df_editado.loc[:, nome] = pd.NA


    # Atualiza as configurações e df_editado no estado da sessão
    ss['configuracoes'] = pd.DataFrame(config_list)
    ss['df_editado'] = df_editado.dropna(how='all').fillna(0).infer_objects(copy=False).copy()  # Garante que df_editado está atualizado e sem nulos

    ss['ação']["recalcular"] = False

    # Exibe o data editor com configurações editáveis
    conf_editadas = st.data_editor(
        data=ss['configuracoes'].copy(),
        column_config=ss['column_config'],
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        disabled=False,
        key='conf_editadas',
        on_change=atualizar_configuracoes
    )

def atualizar_configuracoes():
    edited_rows = st.session_state['conf_editadas'].get("edited_rows", {})

    for idx, alteracoes in edited_rows.items():
        idx = int(idx)
        for coluna, valor in alteracoes.items():
            ss['configuracoes'].at[idx, coluna] = valor

    ss['ação']["recalcular"] = True

def resetar_dfs(tipo='todos'):
    """
    Reseta os dataframes de acordo com o tipo especificado.
    
    Parâmetros:
    - tipo (str): Tipo de reset ('aplicar', 'descartar', 'restaurar', 'resetar_exceto_df_main', 'apagar_tudo')
    """
    if tipo == 'aplicar':
        st.session_state['df_main'] = st.session_state['df_editado'].copy()
        st.session_state['aplicar'] = True
        st.success("Alterações aplicadas com sucesso!")
    elif tipo == 'descartar':
        st.session_state['df_editado'] = st.session_state['df_original'].copy()
        st.success("Alterações descartadas.")
    elif tipo == 'restaurar':
        st.session_state['df_editado'] = st.session_state['df_original'].copy()
        st.success("Séries restauradas.")
    elif tipo == 'resetar_exceto_df_main':
        st.session_state['df_original'] = pd.DataFrame()
        st.session_state['df_editado'] = pd.DataFrame()
        st.session_state['ação'] = {"recalcular": False, "comuns": False, "modificado": False}
        st.success("Reset realizado, exceto para df_main.")
    elif tipo == 'apagar_tudo':
        st.session_state['df_main'] = pd.DataFrame()
        st.session_state['df_original'] = pd.DataFrame()
        st.session_state['df_editado'] = pd.DataFrame()
        st.session_state['ação'] = {"recalcular": False, "comuns": False, "modificado": False}
        st.success("Todos os dataframes foram apagados.")
    else:
        st.error("Tipo de reset desconhecido.")
    
    configuracoes_iniciais()
    st.rerun()  # Use experimental_rerun se st.rerun não estiver disponível



def botoes():
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    # Coluna 1: Toggle para usar intervalo de datas comum
    with col1:
        comuns = st.toggle('Usar intervalo de datas comum')
        if comuns != st.session_state['ação']["comuns"]:
            st.session_state['ação']["comuns"] = comuns
            st.session_state['ação']["modificado"] = True
            st.session_state['ação']["recalcular"] = True
            st.rerun()
    
    # Coluna 2: Aplicar alterações
    with col2:
        if st.button("✅ Aplicar alterações", help='Aplica as edições para o df_main'):
            try:
                resetar_dfs('aplicar')
            except TypeError as e:
                st.error(f"Erro ao aplicar alterações: {e}")
    
    # Coluna 3: Descartar alterações
    with col3:
        if st.button("🗑️ Descartar Alterações"):
            try:
                resetar_dfs('descartar')
            except TypeError as e:
                st.error(f"Erro ao descartar alterações: {e}")
    
    # Coluna 4: Restaurar Séries Aplicadas
    with col4:
        if st.button("⏮️ Restaurar Séries Aplicadas", help='Recupera o estado de df_original, descartando alterações'):
            try:
                resetar_dfs('restaurar')
            except TypeError as e:
                st.error(f"Erro ao restaurar séries: {e}")
    
    # Coluna 5: Resetar exceto df_main
    with col5:
        if st.button("🔄 Resetar exceto df_main"):
            resetar_dfs('resetar_exceto_df_main')
    
    # Coluna 6: Apagar tudo
    with col6:
        if st.button("❌ Apagar tudo"):
            resetar_dfs('apagar_tudo')

if __name__ == '__main__':
    series_manager()
