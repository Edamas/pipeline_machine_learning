import streamlit as st
import pandas as pd

# Função de inicialização do session_state
def initialize_session_state():
    state_variables = {
        # series_manager()
        'df_main': pd.DataFrame(),  # DataFrame principal
        'df_original': pd.DataFrame(),  # DataFrame temporário original
        'df_editado': pd.DataFrame(),  # DataFrame temporário editado
        'configuracoes': pd.DataFrame(),  # DataFrame de configurações - 
        'configuracoes_editadas': pd.DataFrame(),  # DataFrame de configurações editadas após o data_editor
        'name_mapping': {},  # Mapeamento de nomes de séries
        'resetar': False,  # Flag para resetar as configurações
        'aplicar': False,  # aplicar
        "processado": False,  # Flag para indicar se a série foi processada
        "log": [],  # Log para armazenar as operações realizadas
        "metadados": None,  # Para armazenar metadados de séries
        "selected_series": None,  # Para armazenar a série selecionada
        'COLUMN_CONFIG': [],
        'colunas_padrao': ['funcao', 'nome', 'data_min', 'data_max', 'normalizar', 'preencher_nulos', 'media', 'visualizacao'],
        'ação': {"recalcular": True, "comuns": False, "modificado": False},
    }
    """
    Define a configuração das colunas para o Data Editor.
    """
    column_config = {}
    column_config['funcao'] = st.column_config.SelectboxColumn(
        label="Função",
        help='Selecione uma função para esta série: X (variável independente, Input) ou Y (variável dependente, Target)',
        options=['X', 'Y'],
        default='X',
    )
    column_config['nome'] = st.column_config.TextColumn(
        label="Nome",
        disabled=True,
        required=True,
    )
    column_config['data_min'] = st.column_config.DateColumn(
        label="Data mínima",
        format='DD/MM/YYYY',
        required=True,
    )
    column_config['data_max'] = st.column_config.DateColumn(
        label="Data máxima",
        format='DD/MM/YYYY',
        required=True,
    )
    column_config['normalizar'] = st.column_config.CheckboxColumn(
        label='Normalizar',
        help='Selecione para os valores serem ajustados (normalizados) dentro do intervalo 0 e 1',
        #default=False,
    )
    column_config['preencher_nulos'] = st.column_config.SelectboxColumn(
        label='Método de preenchimento de Nulos', 
        options=['Último valor válido', 'Próximo valor válido', 'Média', 'Zeros'],
        help='As análises exigem que não existam valores vazios (nulos). Escolha o método mais apropriado para substituição dos valores não-válidos.',
        default='Último valor válido'
    )
    column_config['media'] = st.column_config.NumberColumn(
        label='Média',
        help='Média entre valores não-nulos da série',
        disabled=True,
    )
    column_config['visualizacao'] = st.column_config.LineChartColumn(
        label='Visualização',
        width=250,
        help='Gráfico de Linhas para a série',
    )
    state_variables['column_config'] = column_config
    
    for key, value in state_variables.items():
        if key not in st.session_state:
            st.session_state[key] = value
