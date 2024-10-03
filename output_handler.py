import streamlit as st

def output_page():
    st.title("Resultados e Relatórios")
    
    # Exibir métricas e gráficos
    st.write("Aqui estão os resultados do modelo treinado:")
    
    # Exemplo de visualização de gráficos ou métricas
    st.write("Acurácia: 95%")
    st.write("Erro médio quadrático: 0.02")
    
    # Exibir gráficos, se aplicável
    st.line_chart([1, 2, 3, 4, 5])
