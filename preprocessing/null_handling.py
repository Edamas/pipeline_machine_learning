import pandas as pd

def tratar_nulos(df, estrategia):
    if estrategia == "Remover Nulos":
        return df.dropna()
    elif estrategia == "Preencher com Zero":
        return df.fillna(0)
    elif estrategia == "Preencher com Último Valor":
        return df.fillna(method="ffill")
    elif estrategia == "Preencher com Próximo Valor":
        return df.fillna(method="bfill")
    elif estrategia == "Preencher com Média":
        return df.fillna(df.mean(numeric_only=True))
    return df
