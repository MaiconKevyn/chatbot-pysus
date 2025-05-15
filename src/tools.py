from langchain_core.tools import tool
from loader import load_raw, load_sus
from typing import Union, Dict, List, Any
import pandas as pd
import numpy as np
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar e verificar dados
_df = load_sus()
logger.info(f"DataFrame carregado: {len(_df)} registros")

# Filtrar apenas diagnósticos que começam com J
_df_filtered = _df[_df.DIAG_PRINC.str.startswith("J")]
logger.info(f"Após filtro de diagnóstico J: {len(_df_filtered)} registros")

# Se o DataFrame filtrado não estiver vazio, use-o; caso contrário, use o original
_df = _df_filtered if not _df_filtered.empty else _df
logger.info(f"DataFrame final: {len(_df)} registros")
# logger.info(f"Colunas disponíveis: {_df.columns.tolist()}")

if 'IDADE' in _df.columns:
    logger.info(f"Valores não-nulos na coluna IDADE: {_df['IDADE'].notna().sum()}")
else:
    logger.error("Coluna IDADE não encontrada no DataFrame!")

_df = _df[_df.DIAG_PRINC.str.startswith("J")]


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

# 2) Parâmetros fixos de bins e labels
_BINS   = [0,10,20,30,40,50,60,70,80,90,float("inf")]
_LABELS = ['0-9','10-19','20-29','30-39','40-49',
           '50-59','60-69','70-79','80-89','90+']

def _compute_age_group_counts(df: pd.DataFrame) -> Dict[str,int]:
    """
    Binning das idades nas faixas fixas e contagem de internações.
    """
    ages = pd.to_numeric(df["IDADE"], errors="coerce").dropna().astype(int)
    ages = ages[(ages >= 0) & (ages <= 120)]
    faixa = pd.cut(ages, bins=_BINS, right=False, labels=_LABELS)
    counts = faixa.value_counts().reindex(_LABELS, fill_value=0)

    # **RETORNE** o dict de faixa -> contagem
    return { label: int(counts[label]) for label in _LABELS }

@tool
def get_admission_age_groups() -> Dict[str, int]:
    """
    Retorna o número de internações por faixa etária (0-9, 10-19, ..., 90+).
    """
    return _compute_age_group_counts(_df)

@tool
def get_top_admission_age_group() -> Dict[str, Union[str,int]]:
    """
    Retorna a faixa etária com o maior número de internações e seu total.
    """
    counts = _compute_age_group_counts(_df)
    top_range = max(counts, key=counts.get)
    return {"age_group": top_range, "count": counts[top_range]}

@tool
def get_top_cities(n: Union[int, str]) -> List[Dict[str, Any]]:
    """
    Retorna as top n cidades com mais internações respiratórias (CID J).

    Parâmetros:
    - n (int ou str): número de cidades a retornar (>= 1).

    Retorno:
    - Lista de dicionários no formato {"cidade": str, "internacoes": int},
      ordenada da cidade com mais internações para menos.
    """
    # 1) Converte e valida n
    try:
        n_int = int(n)
    except (ValueError, TypeError):
        raise ValueError("Parâmetro 'n' deve ser um inteiro válido.")
    if n_int < 1:
        raise ValueError("Parâmetro 'n' deve ser maior ou igual a 1.")

    # 2) Carrega e filtra SUS por CID J
    df = load_sus()
    df = df[df["DIAG_PRINC"].astype(str).str.upper().str.startswith("J")]

    # 3) Conta internações por cidade
    city_counts = (
        df["CIDADE_RESIDENCIA_PACIENTE"]
        .dropna()
        .astype(str)
        .str.strip()
        .value_counts()
    )

    # 4) Pega as top n cidades
    top_n = city_counts.head(n_int)

    # 5) Formata resultado
    return [
        {"cidade": cidade, "internacoes": int(internacoes)}
        for cidade, internacoes in top_n.items()
    ]