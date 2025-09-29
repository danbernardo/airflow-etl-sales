# Smoke test simples: importa o DAG sem precisar do Airflow real.
# Um "smoke test" é um teste rápido para verificar se o código básico funciona,
# sem executar tudo. Aqui, testamos se o DAG 'sales_etl' pode ser importado sem erros,
# simulando o Airflow com "mocks" (versões falsas das bibliotecas). Isso evita precisar
# instalar o Airflow ou rodar containers Docker para um teste simples.
# Útil para desenvolvimento local e CI/CD (integração contínua).
import importlib
import sys
import types

def test_dag_imports_with_fake_airflow(monkeypatch):
    # Cria um objeto falso para simular 'airflow.decorators' (decorators como @dag e @task).
    # O Airflow tem decorators especiais (@dag, @task) para criar pipelines.
    fake_decorators = types.SimpleNamespace()
    def dag(*a, **k):
        def _wrap(f):
            return f  # Retorna a função original sem modificá-la.
        return _wrap
    def task(*a, **k):
        def _wrap(f):
            return f  # Retorna a função original sem modificá-la.
        return _wrap
    fake_decorators.dag = dag
    fake_decorators.task = task
    
    # Simula os módulos do Airflow no sys.modules (sistema de módulos do Python).
    # sys.modules é onde o Python armazena módulos importados. Usamos monkeypatch
    # (do pytest) para "injetar" versões falsas de 'airflow' e 'airflow.decorators'.
    # Isso engana o Python para pensar que o Airflow está instalado, permitindo o import.
    monkeypatch.setitem(sys.modules, "airflow", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "airflow.decorators", fake_decorators)
    
    # Importa o módulo do DAG usando importlib (biblioteca padrão do Python).
    # Em vez de 'import dags.sales_etl', usamos importlib para importar dinamicamente.
    # Isso permite testar o import em um ambiente controlado (com mocks).
    mod = importlib.import_module("dags.sales_etl")
    
    # Verifica se o módulo tem a função 'sales_etl' (nosso DAG).
    # O assert é uma afirmação — se for verdadeira, o teste passa.
    # Aqui, garantimos que o DAG foi definido corretamente no módulo.
    assert hasattr(mod, "sales_etl")