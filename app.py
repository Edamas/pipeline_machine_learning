import streamlit as st
from pages import get_pages
from initialization import initialize_session_state

# Defina a configuração da página
st.set_page_config(page_title="Plataforma de Análise de Dados", layout="wide")

# Função principal para gerenciar a navegação
def main():
    # Inicializa as variáveis do session_state
    initialize_session_state()

    # Gerencia as páginas
    pg = st.navigation(get_pages(), position="sidebar")
    pg.run()

# Início da aplicação
if __name__ == "__main__":
    main()
