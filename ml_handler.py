import streamlit as st

def ml_page():
    st.title("Configuração de Modelos de Machine Learning")
    
    # Escolha do modelo
    model_type = st.selectbox("Escolha o modelo", ["Regressão Linear", "Árvore de Decisão", "Random Forest", "SVM"])
    
    # Parâmetros do modelo
    st.write("Ajuste os parâmetros do modelo:")
    
    if model_type == "Regressão Linear":
        st.slider("Parâmetro 1", 0.0, 1.0)
    elif model_type == "Árvore de Decisão":
        max_depth = st.slider("Profundidade máxima", 1, 20)
    elif model_type == "Random Forest":
        n_estimators = st.slider("Número de árvores", 10, 100)
    elif model_type == "SVM":
        c_value = st.slider("Valor de C", 0.1, 10.0)
    
    # Botão para treinar o modelo
    if st.button("Treinar Modelo"):
        st.write(f"Treinando o modelo {model_type} com os parâmetros selecionados.")
        # Inserir lógica de treinamento de modelo
