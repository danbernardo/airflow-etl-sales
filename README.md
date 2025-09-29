# Projeto Airflow — Exemplo Didático (PT-BR)

Este projeto demonstra um pipeline ETL simples usando Apache Airflow, Pandas e PostgreSQL. O ETL processa dados de vendas de um CSV, transforma-os e salva no banco. É um exemplo educacional para iniciantes em Airflow e Docker.

## Pré-requisitos
- Docker e Docker Compose instalados (versão 3.8+).
- Astro CLI instalado (baixe em https://www.astronomer.io/docs/astro/cli/install-cli).
- Conhecimento básico de linha de comando.
- **Nota**: Este README prioriza o Astro para simplicidade. Se preferir controle manual, use Docker Compose (veja seção alternativa).

## Como Rodar (Local, com Astro — Recomendado)
Siga estes passos para configurar e executar o ambiente usando Astro.

1. **Inicializar o Projeto com Astro**:
   - No diretório do projeto, execute:
     ```
     astro dev init
     ```
   - **Explicação**: Isso configura o projeto Astro, criando arquivos necessários (ex.: Dockerfile, docker-compose.yml automático). Substitui passos manuais de Docker.

2. **Iniciar o Ambiente**:
   - Levante todos os serviços (Airflow + PostgreSQL):
     ```
     astro dev start
     ```
   - Aguarde até ver "Airflow is starting up" e a mensagem de sucesso (leva alguns minutos na primeira vez).
   - **Explicação**: Astro constrói e inicia containers automaticamente, incluindo webserver, scheduler e Postgres. Porta padrão: 8080 para UI.

3. **Acessar a UI do Airflow**:
   - Abra no navegador: http://localhost:8080
   - Login: `admin` / Senha: `admin`
   - **Explicação**: Na UI, localize o DAG `sales_etl_pipeline`. Despause-o (botão "Unpause") e acione manualmente ("Trigger DAG") para executar o ETL.

4. **Verificar o ETL**:
   - Após execução, conecte ao banco: `astro dev psql` (ou manualmente com psql).
   - Execute: `SELECT COUNT(*) FROM vendas;` (deve retornar 950 linhas).
   - **Explicação**: Confirma que o pipeline salvou dados no PostgreSQL.

## Observações
- **DAG e Dependências**: O pipeline em `dags/sales_etl.py` usa Pandas para processar `include/vendas.csv` e salva na tabela `vendas` no PostgreSQL. Astro instala dependências automaticamente via `requirements.txt`.
- **Conexão PostgreSQL**: Criada automaticamente pelo Astro. Para customizar, edite `airflow_settings.yaml` ou use a UI (Admin > Connections > Adicionar `postgres`).
- **Volumes e Persistência**: Astro gerencia volumes para dados e logs, evitando perda entre reinícios.
- **Testes**: Execute `pytest tests/test_dag_import.py` para verificar imports sem rodar o Airflow.

## Solução de Problemas
- **Erro ao Iniciar**: Certifique-se de que portas 8080 e 5432 estão livres. Reinicie com `astro dev restart`.
- **DAG Não Aparece**: Verifique se `dags/sales_etl.py` está em `dags/` e sem erros (veja logs em UI > DAG > Logs).
- **Conexão Falha**: Na UI, teste a conexão `postgres_default`. Se erro, reinicie containers.
- **Limpeza**: Para parar tudo, `astro dev stop`. Para remover containers, `astro dev kill`.

## Alternativa: Como Rodar com Docker Compose (Avançado)
Se preferir controle manual (sem Astro), use o `docker-compose.yml` incluído:
1. Build: `docker compose build`
2. Levantar Postgres: `docker compose up -d postgres`
3. Init DB e criar admin: `docker compose run --rm airflow-webserver airflow db init` + comando de usuário.
4. Subir tudo: `docker compose up -d`
5. Acesse http://localhost:8080.

Para dúvidas, consulte a documentação do Astro/Airflow ou comentários no código.
