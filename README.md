# chatbot-pysus

project-chatbot/
├── data/
│   ├── raw/
│   │   ├── dados_sus3.csv
│   │   ├── IDH_municipios_RS.csv
│   │   ├── poluicao_do_ar_2014_2023.csv
│   │   └── dados_IBGE_modificados.csv
│   └── processed/
│       └── merged_data.parquet
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_prep.py          # ETL e unificação dos dados
│   ├── intents.py            # Definição de intents e slot-filling
│   ├── functions.py          # Funções de domínio (média, total, ranking…)
│   ├── chat_agent.py         # Código de function-calling ou PandasAgent
│   └── app.py                # Interface CLI / FastAPI / Streamlit
│
├── tests/
│   ├── test_data_prep.py
│   ├── test_functions.py
│   └── test_intents.py
│
├── notebooks/
│   └── EDA.ipynb             # Exploração inicial dos dados
│
├── requirements.txt
├── README.md
└── .env                      # Chaves de API, endpoints, etc.
