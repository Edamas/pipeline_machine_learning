import streamlit as st
import pandas as pd

# Função de inicialização do session_state
def initialize_session_state():
    state_variables = {
        "df_series": {},  # Armazenar múltiplas séries
        "df": pd.DataFrame(),  # DataFrame vazio
        "processado": False,  # Inicialize como False
        "log": [],  # Log para armazenar as operações
        "metadados": None,  # Para armazenar metadados de séries
        "selected_series": None,  # Para armazenar a série selecionada
        "df_original": pd.DataFrame(),  # Para armazenar o DataFrame original
    }

    for key, value in state_variables.items():
        if key not in st.session_state:
            st.session_state[key] = value
