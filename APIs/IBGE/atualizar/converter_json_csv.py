import json
import pandas as pd
import streamlit as st

# Configurando o layout do Streamlit
st.set_page_config(layout="wide")

# Função para converter JSON em DataFrame
def json_to_dataframe(json_data):
    records = []
    
    cont = 0
    # Iterar sobre os registros do JSON
    for key, value in json_data.items():
        key = int(key)
        # Processar Classificações e criar uma lista de tuplas com subclassificações
        classificacoes = value.get("Classificações", None)
        if classificacoes:
            classificacoes_list = []
            for cod_classificacao in classificacoes:
                nome_classificacao = classificacoes[cod_classificacao]['nome']
                subclassificacoes = classificacoes[cod_classificacao]['itens']
                for cod_subclassificacao in subclassificacoes:
                    item = f"""(({cod_classificacao}, "{nome_classificacao}"), ({cod_subclassificacao}, "{subclassificacoes[cod_subclassificacao]}"))"""
                    classificacoes_list.append(item)
            value["Classificações"] = classificacoes_list if classificacoes_list else None
        else:
            value["Classificações"] = None
        
        # Converter Variáveis em lista de tuplas
        variaveis = value.get("Variáveis", None)
        variaveis_list = []
        for variavel_cod, variavel_nome in variaveis.items():
            variaveis_list.append(f"""({int(variavel_cod)}, "{variavel_nome.split(' - casas decimais: ')[0]}")""")
        
        value["Variáveis"] = variaveis_list
        
        
            
        # Converter Lista de Períodos em lista de datas
        lista_periodos = value.get("Lista de Períodos", None)
        if lista_periodos:
            value["Lista de Períodos"] = [data for _, data in lista_periodos.items()]
        else:
            value["Lista de Períodos"] = None
        
        # Converter campos de data para datetime no formato dd/mm/aaaa
        for field in ["Última Consulta", "Data Mínima", "Data Máxima"]:
            if field in value and value[field]:
                value[field] = pd.to_datetime(value[field], format="%d/%m/%Y", errors="coerce")
                if not pd.isna(value[field]):
                    value[field] = value[field].strftime("%d/%m/%Y")
                else:
                    value[field] = None
        
        # Converter 'Última atualização' para formato datetime com hora, minuto e segundo
        if "Última atualização" in value and value["Última atualização"]:
            try:
                value["Última atualização"] = pd.to_datetime(value["Última atualização"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
                if not pd.isna(value["Última atualização"]):
                    value["Última atualização"] = value["Última atualização"].strftime("%d/%m/%Y %H:%M")
            except ValueError:
                value["Última atualização"] = None
        
        # Converter números para int/float
        for field in ["Número", "Número de Variáveis", "Número de Períodos", "Número de Registros", "Número de localidades", 
                      "Número de classificações", "Número de subclassificações", "Subtabelas totais", "Quantidade de valores"]:
            if field in value and value[field] is not None:
                try:
                    value[field] = int(value[field])
                except ValueError:
                    value[field] = None
        
        for field in ["Intervalo Coberto (dias)", "Frequência Média (dias)", "Dias sem Registros até Hoje"]:
            if field in value and value[field] is not None:
                try:
                    value[field] = float(value[field])
                except ValueError:
                    value[field] = None
        
        # Processar Níveis Territoriais e criar colunas específicas apenas para os níveis N1, N2, N3 e N6
        niveis_territoriais = value.pop("Níveis Territoriais", None)
        if niveis_territoriais:
            for nivel, detalhes in niveis_territoriais.items():
                if nivel in ["N1", "N2", "N3", "N6"]:
                    coluna = f"""("{nivel}", "{detalhes['Nome']}")"""
                    value[coluna] = []
                    
                    for localidade in detalhes['Localidades Presentes']:
                        localidade_codigo = int(detalhes['Localidades Presentes'][localidade]['Código'])
                        localidade_nome = detalhes['Localidades Presentes'][localidade]['Nome']
                        value[coluna].append(f"""("{localidade_codigo}", "{localidade_nome}")""")
        
        # Adicionar o restante dos valores ao registro
        records.append(value)
    
    # Criar DataFrame a partir dos registros
    df = pd.DataFrame(records)
    
    return df

# Carregando o arquivo JSON
tabelas_json_file = "tabelas_ibge.json"

# Leitura do arquivo JSON
with open(tabelas_json_file, "r", encoding="utf-8") as file:
    tabelas_json = json.load(file)

# Converter JSON para DataFrame
dataframe = json_to_dataframe(tabelas_json)
st.write(dataframe.columns)
dataframe = dataframe[[
'Número', 'Nome', 
'Pesquisa', 'Assunto', 
'Número de Registros', 
'Periodicidade', 'Data Mínima', 'Data Máxima', 'Intervalo Coberto (dias)', 'Frequência Média (dias)',
'Número de Variáveis', 'Variáveis', 
'Número de classificações', 'Número de subclassificações', 'Classificações', 
'Número de localidades', 
'("N1", "Brasil")', 
'("N2", "Grande Região")', 
'("N3", "Unidade da Federação")', 
'("N6", "Município")', 
'Nota', 'Fonte',
'Link de Consulta', 'Última Consulta',
'Dias sem Registros até Hoje', 'Lista de Períodos', 'Última atualização',  'Encerrada', 
]]
dataframe = dataframe.set_index('Número', drop=True)
dataframe.index.name = 'Número'

# Salvar DataFrame em CSV
csv_output_file = "metadados_tabelas.csv"
dataframe.to_csv(csv_output_file, sep='\t', encoding='utf-8', index=True)
st.success(f"Arquivo CSV salvo com sucesso: {csv_output_file}")

# Exibir DataFrame no Streamlit
st.dataframe(dataframe, use_container_width=True)
cont = 0
for i, values in dataframe.iterrows():
    if i == 74:
        for key, values in values.items():
            if type(values) == list:
                {key: [values[0], values[-1]]}
            else:
                {key: values}
        cont += 1