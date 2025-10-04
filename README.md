# Projeto Airflow — Pipeline ETL Robusto

## Sobre o Projeto
Neste projeto, desenvolvi uma arquitetura de dados com o objetivo de processar e analisar o comportamento de vendas de uma empresa através do controle rigoroso de dados de entrada e saída..

O objetivo do projeto é construir uma solução que permitirá à área de vendas acompanhar o fluxo de dados de vendas, monitorar a movimentação de registros, identificar possíveis tendências e desvios, e realizar análises estratégicas para tomada de decisão.

A plataforma escolhida para desenvolvimento do projeto foi o Apache Airflow, utilizando arquitetura ETL (Extract, Transform, Load), que consiste em camadas de extração, transformação e carga, permitindo diversificar o uso de linguagens como Python e SQL para processamento de dados e também possui conexão nativa com PostgreSQL para armazenamento persistente, além de integração com Docker para isolamento e escalabilidade. Também é importante observar que vou armazenar, movimentar e processar somente os dados necessários para o projeto, a fim de monitoramento e custos controlados de infraestrutura.

Esta solução oferece às empresas maior controle sobre sua saúde de vendas, automatização de processos de consolidação de dados e base sólida para planejamento estratégico e crescimento sustentável.

Este projeto demonstra um pipeline ETL completo usando Apache Airflow, Pandas e PostgreSQL. O ETL processa dados de vendas de um CSV, transforma-os e salva no banco, oferecendo uma base sólida para automação de dados em ambientes empresariais.

## Benefícios
Este pipeline ETL traz vantagens reais para empresas que precisam gerenciar dados de vendas de forma eficiente. Veja como ele ajuda no dia a dia:

- **Economia de Tempo e Redução de Erros**: Automatiza tarefas repetitivas, como importar e limpar dados, evitando falhas manuais e liberando a equipe para focar em estratégias de negócio.
- **Crescimento com a Empresa**: Suporta volumes maiores de dados à medida que o negócio cresce, adaptando-se facilmente a novas fontes (como vendas online) ou destinos (relatórios avançados).
- **Dados Confiáveis e Sempre Disponíveis**: Monitora execuções em tempo real e corrige problemas automaticamente, garantindo que informações críticas estejam prontas para decisões rápidas.
- **Qualidade nos Relatórios**: Limpa e organiza dados (ex.: calcula totais de vendas), prevenindo erros em análises financeiras ou dashboards de performance.
- **Custos Mais Baixos**: Diminui a necessidade de trabalho manual, otimizando recursos e reduzindo riscos de perdas ou retrabalho.
- **Aplicações Práticas**: Perfeito para e-commerce ou varejo — por exemplo, atualiza relatórios diários de vendas, alimenta sistemas de marketing ou ajuda a identificar tendências de consumo.

Em resumo, esse projeto transforma dados brutos em ferramentas valiosas para impulsionar vendas e eficiência operacional.



## Pré-requisitos
- Docker e Docker Compose instalados (versão 3.8+).
- Astro CLI instalado (baixe em https://www.astronomer.io/docs/astro/cli/install-cli).
- **Nota**: Este README prioriza o Astro para simplicidade. Se preferir controle manual, use Docker Compose.

## Como Rodar (Local, com Astro — Recomendado)

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
   - Aguarde até ver "Airflow is starting up" e a mensagem de sucesso.
   - Astro constrói e inicia containers automaticamente, incluindo webserver, scheduler e Postgres. Porta padrão: 8080 para UI.

3. **Acessar a UI do Airflow**:
   - Abra no navegador: http://localhost:8080
   - Login: `admin` / Senha: `admin`
   - Na UI, localize o DAG `sales_etl_pipeline`. Acione manualmente ("Trigger DAG") para executar o ETL.

4. **Verificar o ETL**:
   - Após execução, conecte ao banco: `astro dev psql` (ou manualmente com psql).
   - Execute: `SELECT COUNT(*) FROM vendas;`.
   - Confirma que o pipeline salvou dados no PostgreSQL.

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