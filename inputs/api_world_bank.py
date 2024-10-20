import streamlit as st
import pandas as pd
from pre_processing import pre_processing_page

# Funções específicas para o World Bank
def get_world_bank_datasets():
    return {"Crescimento Populacional": 2001, "PIB Mundial": 2002}

def get_world_bank_series_data(series_id, start_date, end_date):
    # Simulação para dados de teste - substituir por requisição à API
    data = [
        {"data": "2000-01-01", "valor": 3.2},
        {"data": "2000-02-01", "valor": 3.1}
    ]
    return data

def api_page_world_bank():
    st.title("API: World Bank")
    datasets = get_world_bank_datasets()
    
    series_name = st.selectbox("Selecione uma série histórica", list(datasets.keys()))
    start_date = st.date_input("Data Inicial", value=pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data Final", value=pd.to_datetime("today"))
    
    if st.button("Buscar Dados"):
        series_id = datasets[series_name]
        data = get_world_bank_series_data(series_id, start_date, end_date)
        df = pd.DataFrame(data)

        st.write("Dados recebidos:")
        st.write(df)

        # Enviar para pré-processamento
        pre_processing_page(df)
