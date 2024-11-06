import streamlit as st

# Função para a Introdução
def mostrar_introducao():
    st.header("🔍 Introdução")
    st.markdown("""
    Bem-vindo à **Documentação** do nosso aplicativo de **Gerenciamento de Séries Temporais**! Este guia irá auxiliá-lo a entender como utilizar as funcionalidades disponíveis de forma eficiente.
    
    **Objetivo**: Facilitar a manipulação, pré-processamento e análise de séries temporais provenientes de diferentes fontes, preparando os dados para modelagem preditiva utilizando regressão.
    """)

# Função para Combinação de Séries
def mostrar_combinacao_series():
    st.header("🔗 Combinação de Séries Temporais")
    st.markdown("""
    Nosso aplicativo permite combinar séries temporais de diferentes fontes, como **BCB**, **IBGE** ou através de **uploads de arquivos**. A combinação adequada das séries enriquece a análise e melhora a performance dos modelos de regressão.
    
    ### **Tipos de Combinação Úteis**
    - **BCB + IBGE**: Combinar indicadores financeiros com dados socioeconômicos.
    - **BCB + Upload do Usuário**: Integrar dados oficiais com informações específicas fornecidas pelo usuário.
    
    ### **Como Combinar Séries**
    1. **Selecione as Séries Desejadas**: Escolha as séries que deseja combinar a partir das fontes disponíveis.
    2. **Defina as Funções**: Marque cada série como **X** (independente) ou **Y** (dependente) conforme a análise desejada.
    3. **Ajuste os Intervalos de Datas**: Alinhe os períodos das séries para garantir consistência temporal.
    4. **Clique em "Aplicar"**: Mescle as séries selecionadas no conjunto principal de dados (**df_main**).
    """)

# Função para Opções do Gerenciador de Séries
def mostrar_opcoes_gerenciador():
    st.header("⚙️ Configurações do Gerenciador de Séries")
    st.markdown("""
    O **Gerenciador de Séries** oferece diversas opções para personalizar o pré-processamento das suas séries temporais:
    
    - **Função X ou Y**: Defina cada série como variável independente (**X**) ou dependente (**Y**).
    - **Intervalos de Datas Personalizados**: Especifique datas de início e término para alinhar todas as séries em um mesmo período.
    - **Datas Comuns**: Ative para forçar todas as séries a compartilharem um intervalo de datas comum.
    - **Normalização**: Normalize os valores das séries para uma escala entre 0 e 1, facilitando comparações e modelagens.
    - **Métodos de Preenchimento de Nulos**:
        - **Último Valor Válido**: Preenche valores ausentes com o último valor disponível.
        - **Próximo Valor Válido**: Preenche valores ausentes com o próximo valor disponível.
        - **Média**: Substitui valores nulos pela média da série.
        - **Zeros**: Preenche valores ausentes com zero.
    
    **Dicas de Uso**:
    - **Datas Comuns**: Utilize esta opção para garantir que todas as séries estejam alinhadas temporalmente.
    - **Normalização**: Recomendado quando as séries possuem escalas diferentes.
    - **Métodos de Preenchimento**: Escolha o método que melhor se adapta à natureza dos seus dados.
    """)

# Função para Conceitos Estatísticos
def mostrar_conceitos_estatisticos():
    st.header("📊 Conceitos Estatísticos")
    st.markdown("""
    Compreender os conceitos estatísticos é fundamental para interpretar corretamente os resultados das análises e previsões realizadas pelo aplicativo.
    
    - **Correlação**: Mede a relação entre duas variáveis, indicando como uma varia em relação à outra.
    - **Determinância (R²)**: Indica a proporção da variabilidade da variável dependente que é explicada pelo modelo de regressão.
    - **Nível de Confiança**: Refere-se à probabilidade de que um intervalo de confiança contenha o valor verdadeiro do parâmetro.
    - **Linha de Regressão**: Representa a tendência central da relação entre as variáveis no modelo de regressão.
    - **Gráficos 2D e 3D**: Visualizações que ajudam a entender a relação entre múltiplas variáveis e os padrões nos dados.
    - **Previsão e Estimativa**: Utilização do modelo de regressão para prever valores futuros da variável dependente com base nos valores das variáveis independentes.
    
    **Importância na Regressão**:
    - **Correlação** ajuda a identificar quais variáveis têm relação significativa com a variável de interesse.
    - **R²** avalia o quão bem o modelo se ajusta aos dados observados.
    - **Níveis de Confiança** fornecem intervalos onde se espera que os parâmetros do modelo estejam.
    - **Visualizações** facilitam a interpretação e a comunicação dos resultados.
    """)

# Função para Exemplos de Operações
def mostrar_exemplos():
    st.header("💡 Exemplos de Operações")
    st.markdown("""
    Aqui estão alguns exemplos de como utilizar o aplicativo para realizar análises e previsões com regressão:
    
    ### 1. **Previsão de Vendas com Regressão Linear**
    - **Selecione a Série de Vendas** como variável **Y**.
    - **Selecione a Série de Marketing** como variável **X**.
    - **Defina o Intervalo de Datas** de janeiro de 2020 a dezembro de 2023.
    - **Ative a Normalização** para ajustar os valores das séries.
    - **Escolha o Método de Preenchimento de Nulos** como "Último Valor Válido".
    - **Clique em "Aplicar"** para processar os dados.
    - **Visualize a Linha de Regressão** no gráfico 2D fornecido.
    
    ### 2. **Combinação de Séries Econômicas**
    - **Faça Upload** de uma série de PIB trimestral.
    - **Combine com a Série de Taxa de Desemprego** fornecida pelo IBGE.
    - **Defina ambas como variáveis X e Y** conforme a análise desejada.
    - **Ajuste as Datas** para um intervalo de 2010 a 2023.
    - **Escolha a Normalização e o Método de Preenchimento de Nulos** adequados.
    - **Aplicar** as configurações e visualizar as correlações e o modelo de regressão.
    
    ### 3. **Previsão Personalizada**
    - **Faça Upload** de sua própria série temporal, como dados de estoque.
    - **Combine com Séries Disponibilizadas** no aplicativo, como vendas ou preços de mercado.
    - **Defina as Configurações** para alinhar as séries.
    - **Processar e Aplicar** para gerar previsões baseadas no modelo de regressão.
    
    **Dicas Finais**:
    - **Experimente Diferentes Combinações de Séries** para explorar como elas influenciam as previsões.
    - **Use as Visualizações** para entender melhor as relações entre as variáveis.
    - **Ajuste as Configurações** conforme necessário para otimizar os resultados das previsões.
    """)

# Função principal para criar a página de Documentação
def documentacao():
    st.title("📘 Documentação do Aplicativo de Séries Temporais")
    st.markdown("Bem-vindo à **Documentação** do nosso aplicativo de **Gerenciamento de Séries Temporais**! Este guia irá auxiliá-lo a entender como utilizar as funcionalidades disponíveis de forma eficiente.")
    
    # Menu de Navegação na Página
    menu = ["🔍 Introdução", "🔗 Combinação de Séries", "⚙️ Configurações", "📊 Conceitos Estatísticos", "💡 Exemplos de Operações"]
    escolha = st.sidebar.radio("Navegação", menu)
    
    # Chamada das funções com base na escolha do usuário
    if escolha == "🔍 Introdução":
        mostrar_introducao()
    elif escolha == "🔗 Combinação de Séries":
        mostrar_combinacao_series()
    elif escolha == "⚙️ Configurações":
        mostrar_opcoes_gerenciador()
    elif escolha == "📊 Conceitos Estatísticos":
        mostrar_conceitos_estatisticos()
    elif escolha == "💡 Exemplos de Operações":
        mostrar_exemplos()

# Executa a função de documentação se o script for chamado diretamente
if __name__ == "__main__":
    documentacao()
