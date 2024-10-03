import streamlit as st
import pandas as pd

# Função genérica para lidar com a API e inputs de gráficos
def api_page(title, get_datasets_func, get_data_func):
    st.title(title)

    # Obter as séries disponíveis da API selecionada
    datasets = get_datasets_func()
    series_name = st.selectbox("Selecione uma série histórica", list(datasets.keys()))
    
    # Datas de início e fim
    start_date = st.date_input("Data Inicial", value=pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data Final", value=pd.to_datetime("today"))
    
    if st.button("Buscar Dados"):
        series_id = datasets[series_name]
        data = get_data_func(series_id, start_date, end_date)
        
        if data:
            df = pd.DataFrame(data)

            # Exibir o DataFrame dentro de um expander
            with st.expander("Exibir tabela de dados", expanded=False):
                st.write(df)

# Funções para as APIs

# Banco Central do Brasil
def get_bcb_datasets():
    return {"Dólar": 1, "IPCA": 433, "PIB": 7326}

def get_bcb_series_data(series_id, start_date, end_date):
    data = [{"data": "2023-01-01", "valor": 5.12}, {"data": "2023-02-01", "valor": 5.21}, {"data": "2023-03-01", "valor": 5.08}]
    return data

def api_page_bcb():
    api_page("API: Banco Central do Brasil", get_bcb_datasets, get_bcb_series_data)

# IBGE
def get_ibge_datasets():
    return {"População": 1001, "PIB": 1002}

def get_ibge_series_data(series_id, start_date, end_date):
    data = [{"data": "2023-01-01", "valor": 210000000}, {"data": "2023-02-01", "valor": 211000000}]
    return data

def api_page_ibge():
    api_page("API: IBGE", get_ibge_datasets, get_ibge_series_data)

# World Bank
def get_world_bank_datasets():
    return {"Crescimento Populacional": 2001, "PIB Mundial": 2002}

def get_world_bank_series_data(series_id, start_date, end_date):
    data = [{"data": "2023-01-01", "valor": 3.2}, {"data": "2023-02-01", "valor": 3.1}]
    return data

def api_page_world_bank():
    api_page("API: World Bank", get_world_bank_datasets, get_world_bank_series_data)

# NOAA
def get_noaa_datasets():
    return {"Temperatura Global": 3001, "Nível do Mar": 3002}

def get_noaa_series_data(series_id, start_date, end_date):
    data = [{"data": "2023-01-01", "valor": 15.5}, {"data": "2023-02-01", "valor": 15.7}]
    return data

def api_page_noaa():
    api_page("API: NOAA", get_noaa_datasets, get_noaa_series_data)
