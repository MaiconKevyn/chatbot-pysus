"""
Módulo para carregar e preparar dados do projeto.
Contém funções para carregamento dos diversos datasets utilizados na análise.
"""
import os
from pathlib import Path
from typing import Tuple

import pandas as pd


def get_project_root() -> Path:
    """
    Retorna o caminho da raiz do projeto independente de onde o script for executado.

    Returns:
        Path: Caminho absoluto para a raiz do projeto
    """
    # Considera que este arquivo está em src/
    return Path(__file__).parent.parent

def load_raw() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Carrega os datasets brutos do projeto.

    Returns:
        Tuple contendo os seguintes DataFrames:
        - sus: Dados do Sistema Único de Saúde
        - idh: Índice de Desenvolvimento Humano dos municípios do RS
        - pol: Dados de poluição do ar
        - ibge: Dados demográficos do IBGE

    Raises:
        FileNotFoundError: Se algum arquivo não for encontrado
    """
    # Obtém o caminho raiz do projeto
    root_path = get_project_root()
    data_dir = root_path / "data" / "raw"

    # Carrega cada dataset com suas configurações específicas
    sus = pd.read_csv(
        data_dir / "dados_sus3.csv",
        parse_dates=["DT_INTER", "DT_SAIDA"],
        low_memory=False
    )

    idh = pd.read_csv(
        data_dir / "IDH_municipios_RS.csv",
        encoding="latin1",
        sep=";"
    )

    pol = pd.read_csv(
        data_dir / "poluicao_do_ar_2014_2023.csv"
    )

    ibge = pd.read_csv(
        data_dir / "dados_IBGE_modificados.csv",
        encoding="latin1",
        sep=";"
    )

    return sus, idh, pol, ibge









# import pandas as pd
#
# def load_raw():
#     sus = pd.read_csv("data/raw/dados_sus3.csv", parse_dates=["DT_INTER","DT_SAIDA"])
#     idh = pd.read_csv("data/raw/IDH_municipios_RS.csv", encoding="latin1", sep = ";")
#     pol = pd.read_csv("data/raw/poluicao_do_ar_2014_2023.csv")
#     ibge = pd.read_csv("data/raw/dados_IBGE_modificados.csv", encoding="latin1", sep = ";")
#     return sus, idh, pol, ibge


# import os
#
#
# def load_raw():
#     # Obter o caminho base do projeto
#     base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
#
#     # Construir caminhos absolutos para os arquivos
#     sus = pd.read_csv(os.path.join(base_path, "data/raw/dados_sus3.csv"),
#                       parse_dates=["DT_INTER", "DT_SAIDA"])
#     idh = pd.read_csv(os.path.join(base_path, "data/raw/IDH_municipios_RS.csv"),
#                       encoding="latin1", sep=";")
#     pol = pd.read_csv(os.path.join(base_path, "data/raw/poluicao_do_ar_2014_2023.csv"))
#     ibge = pd.read_csv(os.path.join(base_path, "data/raw/dados_IBGE_modificados.csv"),
#                        encoding='latin1')  # ou 'cp1252' se 'latin1' não funcionar
#     return sus, idh, pol, ibge