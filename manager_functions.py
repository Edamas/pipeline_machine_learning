# manager_functions.py
import pandas as pd
import streamlit as st
from sklearn.preprocessing import MinMaxScaler

    

def normalizar(serie):
    """
    Normaliza uma série de dados usando MinMaxScaler.
    """
    scaler = MinMaxScaler()
    serie_normalizada = scaler.fit_transform(serie.values.reshape(-1, 1))
    return pd.Series(serie_normalizada.flatten(), index=serie.index)


def preencher_nulos(df_editado, configuracoes):
    """
    Preenche os valores nulos no DataFrame editado conforme as configurações.
    """
    for idx, row in configuracoes.iterrows():
        nome = row['nome']
        metodo = row['preencher_nulos']
        
        if metodo == 'Zeros':
            df_editado[nome] = df_editado[nome].fillna(0)
        elif metodo == 'Média':
            df_editado[nome] = df_editado[nome].fillna(df_editado[nome].mean())
        elif metodo == 'Último valor válido':
            df_editado[nome] = df_editado[nome].fillna(method='ffill')
        elif metodo == 'Próximo valor válido':
            df_editado[nome] = df_editado[nome].fillna(method='bfill')
    
    return df_editado

def ajustar_datas(df_editado, configuracoes, comuns):
    """
    Ajusta os intervalos de datas no DataFrame editado conforme as configurações.
    """
    if comuns:
        data_min_comum = max([df_editado[col].dropna().index.min() for col in df_editado.columns])
        data_max_comum = min([df_editado[col].dropna().index.max() for col in df_editado.columns])
        df_editado = df_editado.loc[data_min_comum:data_max_comum]
    else:
        # Filtragem individual por série
        for col in df_editado.columns:
            data_min = df_editado[col].dropna().index.min()
            data_max = df_editado[col].dropna().index.max()
            df_editado = df_editado.loc[data_min:data_max]
    
    # Substituição de nulos restantes por 0
    df_editado = df_editado.fillna(0)
    
    return df_editado



def get_data_editor_cols():
    """
    Retorna a lista de colunas esperadas no data_editor.
    """
    return ['funcao', 'nome', 'data_min', 'data_max', 'normalizar', 'preencher_nulos', 'media', 'visualizacao']

def preparar_visualizacao(df_editado):
    """
    Prepara os dados para visualização:
    1. Preenche com 0 quaisquer dados faltantes no intervalo geral.
    2. Normaliza os dados entre 0 e 1.
    3. Transforma os dados em listas para cada série.
    4. Atualiza a coluna 'visualizacao' com as listas de valores.
    """
    # Determinar o intervalo geral de datas
    data_min = df_editado.index.min()
    data_max = df_editado.index.max()
    intervalo = pd.date_range(start=data_min, end=data_max, freq='D')
    
    # Reindexar o DataFrame para o intervalo geral e preencher faltantes com 0
    df_reindexed = df_editado.reindex(intervalo, fill_value=0)
    
    # Normalizar os dados entre 0 e 1
    scaler = MinMaxScaler()
    df_normalizado = pd.DataFrame(scaler.fit_transform(df_reindexed), index=df_reindexed.index, columns=df_reindexed.columns)
    
    # Transformar os dados em listas e atualizar a coluna 'visualizacao'
    for col in df_normalizado.columns:
        configuracoes_loc = st.session_state['configuracoes']['nome'] == col
        st.session_state['configuracoes'].loc[configuracoes_loc, 'visualizacao'] = df_normalizado[col].tolist()
    
    return st.session_state['configuracoes']

def aplicar_alteracoes_data_editor(configuracoes, edited_df, df_original):
    """
    Aplica as alterações feitas no data_editor a df_original para gerar df_editado.
    Atualiza as configurações com base em df_editado.

    Parâmetros:
    - configuracoes: DataFrame com as configurações atuais.
    - edited_df: Dicionário contendo 'edited_rows', 'added_rows', 'deleted_rows'.
    - df_original: DataFrame original das séries temporais.

    Retorna:
    - df_editado: DataFrame editado após aplicar as alterações.
    - configuracoes: DataFrame de configurações atualizado.
    """
    df_editado = df_original.copy()
    
    # Aplicar edições nas linhas existentes
    if 'edited_rows' in edited_df:
        for row_idx, changes in edited_df['edited_rows'].items():
            for col, new_value in changes.items():
                if col in df_editado.columns:
                    df_editado.at[row_idx, col] = new_value
    
    # Adicionar novas linhas
    if 'added_rows' in edited_df and edited_df['added_rows']:
        new_rows = pd.DataFrame(edited_df['added_rows'])
        df_editado = pd.concat([df_editado, new_rows], ignore_index=True)
    
    # Deletar linhas
    if 'deleted_rows' in edited_df and edited_df['deleted_rows']:
        df_editado = df_editado.drop(edited_df['deleted_rows'])
        df_editado.reset_index(drop=True, inplace=True)
    
    # Atualizar as configurações com base em df_editado
    configuracoes = ajustar_datas(df_editado, configuracoes, st.session_state.get('comuns', False))
    configuracoes = preencher_nulos(df_editado, configuracoes)
    
    # Normalização
    for idx, row in configuracoes.iterrows():
        nome = row['nome']
        if row['normalizar']:
            df_editado[nome] = normalizar(df_editado[nome])
    
    # Atualização das configurações com as datas válidas e média
    for idx, row in configuracoes.iterrows():
        nome = row['nome']
        serie = df_editado[nome]
        configuracoes.at[idx, 'data_min'] = serie.dropna().index.min()
        configuracoes.at[idx, 'data_max'] = serie.dropna().index.max()
        configuracoes.at[idx, 'media'] = serie.mean()
    
    # Preparar visualização
    configuracoes = preparar_visualizacao(df_editado)
    
    return df_editado, configuracoes

def processar(df_original):
    df_editado = df_original.copy()
    
    # Preenchimento de nulos
    df_editado = preencher_nulos(df_editado, st.session_state['configuracoes'])
    
    # Ajuste de intervalos de datas
    df_editado = ajustar_datas(df_editado, st.session_state['configuracoes'], st.session_state.get('comuns', False))
    
    # Normalização
    for idx, row in st.session_state['configuracoes'].iterrows():
        nome = row['nome']
        if row['normalizar']:
            df_editado[nome] = normalizar(df_editado[nome])
    
    # Atualização das configurações com as datas válidas e média
    for idx, row in st.session_state['configuracoes'].iterrows():
        nome = row['nome']
        serie = df_editado[nome]
        st.session_state['configuracoes'].at[idx, 'data_min'] = serie.dropna().index.min()
        st.session_state['configuracoes'].at[idx, 'data_max'] = serie.dropna().index.max()
        st.session_state['configuracoes'].at[idx, 'media'] = serie.mean()
    
    # Preparar dados para visualização
    st.session_state['configuracoes'] = preparar_visualizacao(df_editado)
    
    return df_editado