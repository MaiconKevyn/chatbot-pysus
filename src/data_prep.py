import pandas as pd

def load_raw():
    sus = pd.read_csv("data/raw/dados_sus3.csv", parse_dates=["DT_INTER","DT_SAIDA"])
    idh = pd.read_csv("data/raw/IDH_municipios_RS.csv")
    pol = pd.read_csv("data/raw/poluicao_do_ar_2014_2023.csv")
    ibge = pd.read_csv("data/raw/dados_IBGE_modificados.csv")
    return sus, idh, pol, ibge
