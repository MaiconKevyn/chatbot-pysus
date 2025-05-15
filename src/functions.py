from loader import load_raw
from langchain_core.tools import tool
from typing import List, Tuple


@tool(parse_docstring=True)
def total_hospitalizations(city: str, year: int) -> int:
    """
    Retorna o total de internações por doenças respiratórias no SUS
    para um dado município e ano.

    Args:
        city: Nome do município (ex.: "Santa Maria")
        year: Ano (ex.: 2020)

    Returns:
        int: Número de internações
    """
    df, df1, df2, df3 = load_raw()
    # filtrar CID-10 J00–J99
    df_resp = df[
        df["DIAG_PRINC"].str.startswith("J", na=False) &
        (df["CIDADE_RESIDENCIA_PACIENTE"].str.lower() == city.lower()) &
        (df["ano"] == year)
        ]
    return int(df_resp.shape[0])


@tool(parse_docstring=True)
def avg_cost(city: str, year: int) -> float:
    """
    Retorna o custo médio das internações no SUS
    para doenças respiratórias em um município e ano.

    Args:
        city: Nome do município
        year: Ano

    Returns:
        float: Valor médio de VAL_TOT
    """
    df = load_sus()
    df_resp = df[
        df["DIAG_PRINC"].str.startswith("J", na=False) &
        (df["CIDADE_RESIDENCIA_PACIENTE"].str.lower() == city.lower()) &
        (df["ano"] == year)
        ]
    return float(df_resp["VAL_TOT"].mean() or 0.0)


@tool(parse_docstring=True)
def mortality_rate(city: str, year: int) -> float:
    """
    Retorna a taxa de mortalidade (MORTE=1) das internações
    no SUS para doenças respiratórias em um município e ano.

    Args:
        city: Nome do município
        year: Ano

    Returns:
        float: Taxa de mortalidade (0.0–1.0)
    """
    df = load_sus()
    df_resp = df[
        df["DIAG_PRINC"].str.startswith("J", na=False) &
        (df["CIDADE_RESIDENCIA_PACIENTE"].str.lower() == city.lower()) &
        (df["ano"] == year)
        ]
    if df_resp.empty:
        return 0.0
    return float(df_resp["MORTE"].sum() / df_resp.shape[0])


@tool(parse_docstring=True)
def top_diagnoses(city: str, year: int, n: int = 5) -> List[Tuple[str, int]]:
    """
    Retorna os principais diagnósticos (CID-10) em internações
    por doenças respiratórias no SUS, ordenados pela frequência.

    Args:
        city: Nome do município
        year: Ano
        n: Número de top diagnósticos

    Returns:
        List[Tuple[str,int]]: Lista de (CID-10, contagem)
    """
    df = load_sus()
    df_resp = df[
        df["DIAG_PRINC"].str.startswith("J", na=False) &
        (df["CIDADE_RESIDENCIA_PACIENTE"].str.lower() == city.lower()) &
        (df["ano"] == year)
        ]
    top = (
        df_resp.groupby("DIAG_PRINC").size()
        .nlargest(n)
        .reset_index(name="count")
    )
    return list(top.itertuples(index=False, name=None))
