import streamlit as st

# Função para carregar arquivos
def upload_files():
    st.title("Upload de Arquivos")
    
    # Upload de múltiplos arquivos
    uploaded_files = st.file_uploader("Selecione os arquivos para upload", accept_multiple_files=True)

    if uploaded_files:
        st.write(f"{len(uploaded_files)} arquivo(s) carregado(s) com sucesso!")
        for file in uploaded_files:
            st.write(f"Arquivo: {file.name}")
