import streamlit as st
from inputs.user_input import user_input
from processing.regression import regression_page
from sobre import sobre
from documentacao import documentacao
from inputs.api_bcb import *
from inputs.api_acoes import *
from inputs.api_ibge import *
from inputs.metadados.get_metadata_yahoo import get_yahoo_metadata

def get_pages():
    return {
        "1️⃣FONTES DE DADOS:": [],
        "Upload do Usuário": [
            st.Page(user_input, title='Carregar Dados do Usuário (Upload)', icon="📥", url_path="carregar-dados", default=True),
        ],
        'IBGE': [
            st.Page(contas_nacionais_pib, title="Contas Nacionais e PIB", icon="🌐", url_path="agropecuaria"),
        ],
        'Banco Central do Brasil': [
            st.Page(autoridade_monetaria, title="Autoridade Monetária", icon="💸", url_path="autoridade-monetaria"),
            st.Page(base_monetaria, title="Base Monetária", icon="💵", url_path="base-monetaria"),
            st.Page(cambio, title='Câmbio', icon="💱", url_path="cambio"),
            st.Page(comercio_exterior, title='Comércio Exterior', icon="🚢", url_path="comercio-exterior"),
            st.Page(confianca_expectativas_metas, title='Confiança, Expectativas e Metas', icon="📈", url_path="confianca-expectativas-metas"),
            st.Page(fatores_condicionantes_da_base_monetaria, title='Fatores Condicionantes da Base Monetária', icon="🔎", url_path="fatores-condicionantes-base-monetaria"),
            st.Page(industria_de_veiculos, title='Indústria de Veículos', icon="🚗", url_path="industria-de-veiculos"),
            st.Page(juros, title='Juros', icon="📊", url_path="juros"),
            st.Page(mercado_de_trabalho, title='Mercado de Trabalho', icon="👷", url_path="mercado-de-trabalho"),
            st.Page(poupanca, title='Poupança', icon="🏦", url_path="poupanca"),
            st.Page(precos_e_indices_gerais_inflacao, title='Preços e Índices Gerais (Inflação)', icon="📉", url_path="precos-indices-gerais-inflacao"),
            st.Page(precos_e_indices_por_setor_inflacao, title='Preços e Índices por Setor (Inflação)', icon="🏭", url_path="precos-indices-por-setor-inflacao"),
            st.Page(regulacao_volatilidade_e_risco, title='Regulação, Volatilidade e Risco', icon="📜", url_path="regulacao-volatilidade-risco"),
            st.Page(reservas_internacionais, title='Reservas Internacionais', icon="🌎", url_path="reservas-internacionais"),
        ],
        "Yahoo Finance": [
            st.Page(crypto, title="Criptomoedas", icon="🪙", url_path="crypto"),
            st.Page(currency, title="Moedas", icon="💵", url_path="currency"),
            st.Page(equity, title="Ações", icon="📈", url_path="equity"),
            st.Page(etf, title="ETFs", icon="📊", url_path="etf"),
            st.Page(future, title="Futuro (Opções)", icon="🕰️", url_path="future"),
            st.Page(index, title="Índices", icon="📋", url_path="index"),
            st.Page(mutualfund, title="Fundos Mútuos", icon="💼", url_path="mutualfund"),
        ],
        '---------------------------': [],
        "2️⃣Processamento": [
            st.Page(regression_page, title="Regressão", icon="📉", url_path="regressao"),
        ],
        '---------------------------': [],
        'Ajuda': [
            st.Page(sobre, title='Sobre', icon='ℹ️', url_path="sobre"),
            st.Page(documentacao, title='Sobre valores nulos', icon='📖', url_path="documentacao"),
            st.Page(get_yahoo_metadata, title='Capturar Metadados do Yahoo', icon='📊', url_path="metadados-yahoo"),
        ]
    }

