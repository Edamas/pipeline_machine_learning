import streamlit as st
from inputs.BANCO_CENTRAL.api_bcb import api_page_bcb
from inputs.IBGE.api_ibge import api_ibge
from inputs.ACOES.api_acoes import api_acoes
from inputs.user_input import user_input
#from inputs.api_world_bank import api_page_world_bank
#from inputs.api_noaa import api_page_noaa
from preprocessing.analysis import analysis_page
from preprocessing.date_handling import date_handling_page
from preprocessing.value_handling import value_handling_page
from pre_processing import pre_processing_page
from correlation import correlation_page

def get_pages():
    return {
        "Entrada": [
            st.Page(user_input, title='Input do Usuário'),
            st.Page(api_page_bcb, title="API: Banco Central do Brasil"),
            st.Page(api_ibge, title="API: IBGE"),
            st.Page(api_acoes, title='API: Ações'),
            #st.Page(api_page_world_bank, title="API: World Bank"),
            #st.Page(api_page_noaa, title="API: NOAA"),
        ],
        "Pré-Processamento": [
            st.Page(date_handling_page, title="Manipulação de Datas"),
            st.Page(value_handling_page, title="Manipulação de Valores"),
            st.Page(pre_processing_page, title="Pré-Processamento de Dados")
        ],
        "Análise": [
            st.Page(analysis_page, title="Análise de Dados"),
            st.Page(correlation_page, title="Correlações"),
        ],
    }
