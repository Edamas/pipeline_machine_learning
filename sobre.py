import streamlit as st
import graphviz

# Função para gerar o fluxograma com o loop de interação entre usuário e dados
def criar_fluxograma():
    dot = graphviz.Digraph(comment='Fluxograma Atualizado do Projeto')

    # Configurações globais do grafo
    dot.attr(rankdir='TB', size='12')  # Fluxo da esquerda para direita (Left -> Right)
    dot.attr('node', shape='box')  # Usar caixas retangulares para os nós

    # Usuário no topo
    dot.node('U', label='Usuário', style='filled', color='coral')

    # Frontend e Botões de Controle
    with dot.subgraph(name='cluster_frontend') as frontend:
        frontend.attr(label='FrontEnd', style='filled', color='lightyellow')
        frontend.node('manager', 'Gerenciador de Séries\n[data_editor]')
        frontend.node('normalizar', 'Normalizar\nvalores\n[checkbox]')
        frontend.node('data_min', 'Data Mínima\n[date_input]')
        frontend.node('data_max', 'Data Máxima\n[date_input]')
        frontend.node('nulos', '"Tratatamento\nde nulos"\n[selectbox]')
        frontend.node('novas_series', '"Seleção\nde Séries"\n[dataframe]')
        frontend.node('comuns', '"Usar datas\ncomuns"\n[toggle]')
        frontend.node('aplicar', '[button]\nAplicar')
        
    with dot.subgraph() as same_rank:
        same_rank.attr(rank='same')
        same_rank.node('configuracoes', 'Configurações')
        
        same_rank.node('processamento', 'Processamento')
        
    # Agrupamento dos DataFrames
    with dot.subgraph(name='Backend') as dataframes:
        dataframes.attr(label='BackEnd', style='filled', color='lightblue', same_rank='same')
        dataframes.attr(rank='same')
        dataframes.node('df_main', 'df_main\n(séries de df_editado aplicados)')
        dataframes.node('df_editado', 'df_editado\n(df_original com ajustes do usuário)')
        dataframes.node('df_original', 'df_original\n(combina df_main com novas séries)')
        
    
    # Definindo o rank para manter df_main e df_editado no mesmo nível
    with dot.subgraph() as same_rank:
        same_rank.attr(rank='same')
        same_rank.node('df_main')
        same_rank.node('df_original')
        same_rank.node('df_editado')
        same_rank.node('manager')
    
    # Adicionando arestas (setas) entre os elementos para definir o fluxo
    dot.edge('U', 'comuns')
    dot.edge('comuns', 'processamento')
    dot.edge('df_editado', 'configuracoes')
    dot.edge('U', 'novas_series')
    dot.edge('U', 'nulos')
    dot.edge('U', 'data_min')
    dot.edge('data_min', 'manager', dir='both')
    dot.edge('U', 'data_max')
    dot.edge('data_max', 'manager', dir='both')
    dot.edge('U', 'normalizar')
    dot.edge('novas_series', 'df_original')
    dot.edge('df_main', 'df_original')
    dot.edge('df_original', 'processamento')
    dot.edge('processamento', 'df_editado')
    dot.edge('configuracoes', 'manager', dir='both')
    dot.edge('normalizar', 'manager', dir='both')
    dot.edge('nulos', 'manager', dir='both')
    dot.edge('configuracoes', 'processamento')
    dot.edge('df_editado', 'aplicar')
    dot.edge('aplicar', 'df_main')
    dot.edge('U', 'aplicar')

    return dot

# Função para mostrar o fluxograma
def mostrar_fluxograma():
    st.subheader("📊 Fluxograma do Processo")
    st.write("Este fluxograma representa o fluxo de dados e operações no pipeline de Machine Learning utilizado neste projeto.")
    fluxograma = criar_fluxograma()
    st.graphviz_chart(fluxograma.source)

# Função para as Configurações
def mostrar_configuracoes():
    st.subheader("⚙️ Configurações das Séries Temporais")
    st.write("Defina aqui parâmetros importantes como:")
    st.markdown("""
    - **Data Mínima e Máxima**: Intervalo de tempo para a análise.
    - **Normalizar Valores**: Transformar dados para a faixa entre 0 e 1.
    - **Preenchimento de Nulos**: Método de preenchimento de dados ausentes.
    """)
    st.write("Essas configurações influenciam diretamente como os dados serão processados e analisados.")

# Função para o Data Editor
def mostrar_data_editor():
    st.subheader("📝 Editor de Dados")
    st.write("Interaja diretamente com as séries temporais e ajuste valores específicos. O **Editor de Dados** permite:")
    st.markdown("""
    - Seleção e edição de séries de interesse.
    - Ajuste de intervalos de datas e tratamento de valores nulos.
    - Aplicação de métodos de normalização para preparar dados para análise.
    """)
    st.info("Após as edições, os dados são enviados para o processo de transformação.")

# Função para Processamento
def mostrar_processamento():
    st.subheader("🔄 Processamento de Dados")
    st.write("O processamento aplica as configurações ao **DataFrame Original (df_original)**, preenchendo valores nulos, normalizando e filtrando as séries temporais com base nas escolhas feitas pelo usuário.")
    st.write("O resultado é o **DataFrame Editado (df_editado)**, pronto para o próximo estágio de análise ou modelagem.")



# Função para apresentar informações sobre o projeto
def sobre_o_projeto():
    st.subheader("📚 Sobre o Projeto")
    st.write("Este é um pipeline de Machine Learning desenvolvido para o **Projeto Integrador IV** do curso de **Computação** na **Univesp**.")
    st.write("O projeto utiliza técnicas de pré-processamento de séries temporais, como normalização, tratamento de dados ausentes e intervalos de data, que são etapas fundamentais para modelagem preditiva.")
    st.markdown("""
    ### Objetivo
    Fornecer uma interface intuitiva para a seleção e manipulação de séries temporais, facilitando o fluxo de trabalho de pré-processamento de dados para uso em modelos de Machine Learning.
    """)
    st.markdown("### Público-Alvo")
    st.write("Estudantes e profissionais de Ciência de Dados e Machine Learning, especialmente aqueles interessados em manipulação e análise de séries temporais.")
    st.markdown("### Ferramentas e Técnicas")
    st.write("""
    - **Linguagem**: Python
    - **Bibliotecas**: Streamlit, Pandas, Graphviz
    - **Assistência**: Cursos universitários, pesquisas e o ChatGPT (apesar de ser um pouco insistente... 😅)
    """)

# Função para detalhes dos autores do projeto
def sobre_os_autores():
    st.subheader("👥 Sobre os Autores")
    st.write("Este projeto foi desenvolvido por um grupo de estudantes com o objetivo de aplicar conhecimentos em ciência de dados e desenvolvimento de pipelines de machine learning.")
    for i in range(1, 5):
        st.markdown(f"""
        **Autor {i}**
        - **Nome**: 
        - **Registro Acadêmico (RA)**: 
        - **GitHub**: [GitHub do Autor {i}](https://github.com)
        - **Curso**: Computação
        - **Sobre mim**: Pequeno resumo ou email para contato.
        """)

# Função de instruções de uso
def instrucoes_de_uso():
    st.subheader("🚀 Instruções de Uso")
    st.markdown("""
    1. **Escolha das Séries Temporais**: Inicie selecionando as séries desejadas no painel de **Fontes de Dados** à esquerda.
    2. **Configuração**: Ajuste as configurações das séries temporais, incluindo datas mínimas e máximas, normalização e tratamento de nulos.
    3. **Editor de Dados**: Revise e altere dados específicos no editor, se necessário.
    4. **Processamento**: Execute o processamento, que aplicará as configurações definidas.
    5. **Salvar**: Use o botão **Aplicar** para salvar o estado final em `df_main` para uso em modelos de Machine Learning.
    """)


# Função para criar a página inteira
def sobre():
    st.title("📈 Gerenciamento de Séries Temporais")
    st.write("Bem-vindo ao pipeline de manipulação e pré-processamento de séries temporais!")
    
    # Sessões do projeto
    sobre_o_projeto()
    mostrar_fluxograma()
    instrucoes_de_uso()
    mostrar_configuracoes()
    mostrar_data_editor()
    mostrar_processamento()
    sobre_os_autores()
