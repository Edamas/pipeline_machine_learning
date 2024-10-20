import streamlit as st
import pandas as pd
from pre_processing import pre_processing_page

# Funções específicas para o NOAA
def get_noaa_datasets():
    return {"Temperatura Global": 3001, "Nível do Mar": 3002}

def get_noaa_series_data(series_id, start_date, end_date):
    # Simulação para dados de teste - substituir por requisição à API
    data = [
        {"data": "2023-01-01", "valor": 15.5},
        {"data": "2023-02-01", "valor": 15.7}
    ]
    return data

def api_page_noaa():
    st.title("API: NOAA")
    datasets = get_noaa_datasets()
    
    series_name = st.selectbox("Selecione uma série histórica", list(datasets.keys()))
    start_date = st.date_input("Data Inicial", value=pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data Final", value=pd.to_datetime("today"))
    
    if st.button("Buscar Dados"):
        series_id = datasets[series_name]
        data = get_noaa_series_data(series_id, start_date, end_date)
        df = pd.DataFrame(data)

        st.write("Dados recebidos:")
        st.write(df)

        # Enviar para pré-processamento
        pre_processing_page(df)
