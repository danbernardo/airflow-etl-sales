# Importações: Aqui carregamos bibliotecas necessárias para o código funcionar.
# - logging: Para registrar mensagens (logs) durante a execução, ajudando a depurar erros.
# - os: Para acessar variáveis do sistema (como caminhos de arquivos).
# - pandas (pd): Biblioteca para trabalhar com dados em tabelas (DataFrames), como ler CSVs.
# - pathlib.Path: Para lidar com caminhos de arquivos de forma segura.
# - typing: Para definir tipos de dados (ex.: List[Dict]), tornando o código mais claro.
# - datetime e timedelta: Para trabalhar com datas e intervalos de tempo (ex.: agendamento).
# - airflow.decorators: Ferramentas do Airflow para criar DAGs e tarefas de forma simples.
# - PostgresHook: Conector do Airflow para se conectar ao banco de dados PostgreSQL.
import logging
import os
import pandas as pd

from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Configuração de logging: Define o nível de mensagens (INFO) para registrar informações úteis.
# Isso ajuda a ver o que está acontecendo durante a execução, como quantas linhas foram processadas.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Constantes: Valores fixos usados no código.
# - START_DATE: Data de início do DAG (quando ele começa a rodar).
# - PG_CONN_ID: ID da conexão com o PostgreSQL no Airflow (definida na UI como "postgres").
# - SALES_CSV_ENV: Nome da variável de ambiente para sobrescrever o caminho do CSV, se necessário.
START_DATE = datetime(2025, 1, 1)
PG_CONN_ID = "postgres"
SALES_CSV_ENV = "SALES_CSV"

# DAG (Directed Acyclic Graph): É o "plano" do pipeline no Airflow.
# - dag_id: Nome único do pipeline.
# - start_date: Quando começa.
# - schedule: Frequência (aqui, "@daily" = todos os dias).
# - catchup: Se deve executar execuções passadas (False = não).
# - tags: Etiquetas para organizar (ex.: "etl" para extração/transformação/carga).
@dag(
    dag_id="sales_etl_pipeline",
    start_date=START_DATE,
    schedule="@daily",
    catchup=False,
    tags=["etl", "sales"],
)
def sales_etl():
    """
    Pipeline simples: extract -> transform -> load.
    
    Explicação: Um pipeline ETL (Extract, Transform, Load) é como uma receita:
    - Extract: Pega dados de uma fonte (aqui, um arquivo CSV).
    - Transform: Limpa e organiza os dados (ex.: calcula totais).
    - Load: Salva os dados em um banco (aqui, PostgreSQL).
    Este DAG roda essas etapas em sequência todos os dias.
    """

    # Tarefa 1: Extract (Extração)
    # - Lê o arquivo CSV e retorna os dados como uma lista de dicionários.
    # - Retries: Tenta novamente 1 vez se falhar, com delay de 1 minuto.
    @task(retries=1, retry_delay=timedelta(minutes=1))
    def extract() -> List[Dict]:
        # Define o caminho padrão do CSV dentro do container Docker do Airflow.
        # No Astro, arquivos em "include/" são acessíveis. Se a variável SALES_CSV_ENV estiver definida, usa ela.
        default = Path("/usr/local/airflow/include/vendas.csv")
        csv_path = Path(os.getenv(SALES_CSV_ENV, str(default)))

        # Verifica se o arquivo existe. Se não, lança erro para parar o pipeline.
        if not csv_path.exists():
            raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_path}")

        # Lê o CSV com pandas e registra quantas linhas foram extraídas.
        df = pd.read_csv(csv_path)
        logger.info("Extraído %d linhas do CSV", len(df))
        return df.to_dict(orient="records")  # Converte para lista de dicionários (fácil de passar para outras tarefas).

    # Tarefa 2: Transform (Transformação)
    # - Limpa e organiza os dados: converte tipos, calcula totais, remove inválidos.
    @task
    def transform(rows: List[Dict]) -> List[Dict]:
        # Converte a lista de dicionários em um DataFrame do pandas (como uma tabela).
        df = pd.DataFrame(rows)
        
        # Define colunas obrigatórias (se faltar alguma, erro).
        required = {"sale_id", "product", "quantity", "price", "sale_date"}
        if not required.issubset(set(df.columns)):
            raise ValueError(f"Colunas obrigatórias ausentes: {required - set(df.columns)}")

        # Converte tipos de dados para garantir consistência (ex.: números inteiros).
        df["sale_id"] = df["sale_id"].astype(int)
        df["quantity"] = df["quantity"].astype(int)
        df["price"] = df["price"].astype(float)
        # Converte data para string no formato YYYY-MM-DD (compatível com banco).
        df["sale_date"] = pd.to_datetime(df["sale_date"]).dt.strftime("%Y-%m-%d")
        # Calcula total: quantidade * preço.
        df["total"] = df["quantity"] * df["price"]

        # Remove linhas com valores vazios nas colunas obrigatórias.
        df = df.dropna(subset=["sale_id", "quantity", "price", "sale_date"])
        logger.info("Transformado %d linhas válidas", len(df))
        return df.to_dict(orient="records")

    # Tarefa 3: Load (Carga)
    # - Salva os dados no PostgreSQL.
    # - Retries: Tenta 2 vezes se falhar, com delay de 5 minutos.
    # - Timeout: Para se demorar mais de 1 hora.
    @task(
        retries=2,
        retry_delay=timedelta(minutes=5),
        execution_timeout=timedelta(hours=1),
    )
    def load(rows: List[Dict]) -> None:
        logger.info("Recebidas %d linhas para carregar", len(rows))
        if not rows:
            logger.info("Nenhuma linha para carregar.")
            return

        # Conecta ao PostgreSQL usando o hook do Airflow.
        hook = PostgresHook(postgres_conn_id=PG_CONN_ID)
        conn = hook.get_conn()
        
        # SQL para criar a tabela se não existir (com colunas definidas).
        create_sql = """
        CREATE TABLE IF NOT EXISTS vendas (
            sale_id INTEGER PRIMARY KEY,  -- ID único da venda.
            product VARCHAR(255),         -- Nome do produto.
            category VARCHAR(255),        -- Categoria (ex.: Roupas).
            region VARCHAR(255),          -- Região (ex.: Sul).
            quantity INTEGER,             -- Quantidade vendida.
            price FLOAT,                  -- Preço unitário.
            sale_date DATE,               -- Data da venda.
            total FLOAT                   -- Total calculado (quantidade * preço).
        );
        """
        with conn.cursor() as cur:
            cur.execute(create_sql)
        conn.commit()
        logger.info("Tabela vendas criada/verificada")

        # Prepara os dados para inserção (lista de tuplas).
        values = [
            (
                r["sale_id"],
                r["product"],
                r["category"],
                r["region"],
                r["quantity"],
                r["price"],
                r["sale_date"],
                r["total"],
            )
            for r in rows
        ]
        logger.info("Preparadas %d linhas para inserção", len(values))

        # SQL para inserir dados, ignorando duplicatas (ON CONFLICT).
        insert_sql = """
        INSERT INTO vendas (sale_id, product, category, region, quantity, price, sale_date, total)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (sale_id) DO NOTHING;
        """
        with conn.cursor() as cur:
            cur.executemany(insert_sql, values)
            conn.commit()
        logger.info("Carregadas %d linhas (ignorando duplicatas)", len(values))

    # Fluxo do DAG: Define a ordem das tarefas (extract -> transform -> load).
    raw = extract()
    cleaned = transform(raw)
    load(cleaned)

# Executa o DAG: Isso registra o pipeline no Airflow para ser executado.
sales_etl()
