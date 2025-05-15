from langchain_core.tools import tool
from loader import load_raw, load_sus
from typing import Union, Dict, List
import pandas as pd
import numpy as np


_df = load_sus()

@tool
def get_max_age() -> int:
    """
    Retorna a maior idade registrada no conjunto de dados (`IDADE`).
    """
    # Remove valores nulos e converte para inteiro
    ages = _df["IDADE"].dropna().astype(int)
    if ages.empty:
        raise ValueError("Não há dados de idade disponíveis.")
    return int(ages.max())


@tool
def get_top_ages(
    n: Union[int, str],
    range: str
) -> Union[List[int], Dict[str, List[int]], Dict[str, str]]:
    """
    Retorna as top n idades únicas no conjunto de dados (`IDADE`).

    Parâmetros:
    - n (int ou str): número de idades a retornar (>= 1).
    - range (str):
        * 'menores' → n menores idades únicas,
        * 'maiores' → n maiores idades únicas,
        * 'ambos'    → retorna {'menores': [...], 'maiores': [...]}.

    Exemplo:
        get_top_ages(n=5, range='menores') → [0, 1, 2, 3, 4]
    """
    # Carrega e limpa
    ages = pd.to_numeric(_df["IDADE"], errors="coerce").dropna().astype(int)
    if ages.empty:
        return {"error": "Não há dados de idade disponíveis."}

    # Converte n para inteiro, se vier como string
    try:
        n_int = int(n)
    except (ValueError, TypeError):
        return {"error": "Parâmetro 'n' deve ser um inteiro ou string numérica."}
    if n_int < 1:
        return {"error": "O parâmetro 'n' deve ser >= 1."}

    # Normaliza opção de range
    opt = range.strip().lower()
    if opt not in ("menores", "maiores", "ambos"):
        return {"error": "Parâmetro 'range' inválido. Use 'menores', 'maiores' ou 'ambos'."}

    # Extrai apenas valores únicos, ordenados
    unique_ages = sorted(set(ages.tolist()))

    # Função auxiliar para fatiar
    def slice_ages(desc: bool):
        lst = unique_ages[::-1] if desc else unique_ages
        return lst[:n_int]

    # Retorna conforme solicitado
    if opt == "menores":
        return slice_ages(desc=False)
    elif opt == "maiores":
        return slice_ages(desc=True)
    else:  # ambos
        return {
            "menores": slice_ages(desc=False),
            "maiores": slice_ages(desc=True)
        }
@tool
def get_admission_age_groups() -> Dict[str, Dict[str, Union[int, float]]]:
    """
    Retorna a distribuição de internações por faixa etária (0-9, 10-19, ..., 90+),
    incluindo contagem exata e porcentagem relativa, ordenada pelas faixas com mais internações.
    """
    # 1) extrai e limpa as idades
    ages = pd.to_numeric(_df["IDADE"], errors="coerce").dropna().astype(int)
    if ages.empty:
        return {}
    # filtra idades plausíveis
    ages = ages[(ages >= 0) & (ages <= 120)]

    # 2) configura bins e labels
    bins = list(range(0, 100, 10)) + [np.inf]
    labels = [f"{i}-{i + 9}" for i in range(0, 90, 10)] + ["90+"]

    # 3) categoriza e conta
    groups = pd.cut(ages, bins=bins, right=False, labels=labels)
    counts = groups.value_counts().reindex(labels, fill_value=0)
    total = int(counts.sum())

    # 4) monta resultado ordenado descendentemente
    sorted_labels = counts.sort_values(ascending=False).index.tolist()
    result: Dict[str, Dict[str, Union[int, float]]] = {}
    for label in sorted_labels:
        cnt = int(counts[label])
        pct = round(cnt / total * 100, 2) if total > 0 else 0.0
        result[label] = {"count": cnt, "percent": pct}

    return result

# def get_mortality_rate(city: str, year: int) -> Union[float, Dict[str, str]]:
#     """
#     Retorna a taxa de mortalidade hospitalar por 1.000 internações
#     em uma dada cidade e ano, usando o DataFrame `_df` carregado
#     de `dados_sus3.csv`.
#     """
#     df = _df.copy()
#     # converte DT_INTER de int/str para datetime e extrai o ano
#     df["DT_INTER"] = pd.to_datetime(df["DT_INTER"].astype(str), format="%Y%m%d", errors="coerce")
#     df["ano"] = df["DT_INTER"].dt.year
#
#     # filtro case-insensitive na cidade
#     mask_city = df["CIDADE_RESIDENCIA_PACIENTE"].str.lower() == city.lower()
#     mask_year = df["ano"] == year
#     sub = df[mask_city & mask_year]
#
#     if sub.empty:
#         return {"error": f"Sem dados de internações para '{city}' em {year}"}
#
#     total_internacoes = len(sub)
#     total_mortes      = int(sub["MORTE"].sum())
#
#     if total_internacoes == 0:
#         return {"error": f"Nenhuma internação registrada para '{city}' em {year}"}
#
#     rate = total_mortes / total_internacoes * 1000
#     return round(rate, 2)

# @tool
# def get_names_unique_city():
#     """
#     Retorna uma lista de cidades únicas.
#     """
#     _df = load_raw()
#     return _df["CIDADE_RESIDENCIA_PACIENTE"].unique().tolist()