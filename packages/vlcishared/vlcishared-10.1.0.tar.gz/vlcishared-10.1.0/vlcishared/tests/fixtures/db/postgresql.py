from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, text

from vlcishared.env_variables.secrets import get_secret


@pytest.fixture
def mock_postgres_patch(monkeypatch, connection):
    """
    Fixture que mockea PostgresConnector para ejecutar queries sobre una base de datos real (SQLite/PostgreSQL de prueba).

    - Redirige métodos como connect, execute y execute_query al engine de pruebas.
    - Permite testear sin conectarse a una base de datos real de producción.
    - Requiere la ruta del import de PostgresConnector.

    Parámetros:
    - ruta_importacion (str): Ruta completa donde se importa `PostgresConnector` (ej. "mi_paquete.mi_modulo.PostgresConnector").
    - execute_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `execute`.
    - execute_query_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `execute_query`.
    - call_procedure_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `call_procedure`.
    - execute_multiple_queries_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `execute_multiple_queries`.
    - insert_query_commit_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `insert_query_commit`.

    Uso:
        def test_xxx(mock_db_patch):
            mock_db = mock_db_patch("modulo.donde.importa.PostgresConnector")
            mock_db.execute.assert_called_once()
    """

    def _patch(
        target_path: str,
        execute_side_effect=None,
        execute_query_side_effect=None,
        call_procedure_side_effect=None,
        execute_multiple_queries_side_effect=None,
        insert_query_commit_side_effect=None,
    ):
        mock_connector = MagicMock()

        mock_connector.connect.return_value = connection
        mock_connector.close.return_value = None

        mock_connector.execute.side_effect = execute_side_effect or execute_side_effect_default(connection)
        mock_connector.execute_query.side_effect = execute_query_side_effect or execute_query_side_effect_default(connection)
        mock_connector.call_procedure.side_effect = call_procedure_side_effect or call_procedure_side_effect_default(connection)
        mock_connector.execute_multiple_queries.side_effect = execute_multiple_queries_side_effect or execute_multiple_queries_side_effect_default(connection)
        mock_connector.insert_query_commit.side_effect = insert_query_commit_side_effect or insert_query_commit_side_effect_default(connection)

        monkeypatch.setattr(target_path, lambda *args, **kwargs: mock_connector)
        return mock_connector

    yield _patch


@pytest.fixture
def connection():
    """
    Crea una conexión de SQLAlchemy contra una base de datos PostgreSQL de prueba.

    - Devuelve una conexión viva que se cierra al finalizar el test.
    - Usado por otros fixtures para ejecutar queries reales en un entorno aislado.
    """
    user = get_secret("GLOBAL_DATABASE_POSTGIS_LOGIN_TEST")
    password = get_secret("GLOBAL_DATABASE_POSTGIS_PASSWORD_TEST")
    port = get_secret("GLOBAL_DATABASE_POSTGIS_PORT_TEST")
    host = get_secret("GLOBAL_DATABASE_POSTGIS_HOST_TEST")
    database = get_secret("GLOBAL_DATABASE_POSTGIS_DATABASE_TEST")
    schema = get_secret("GLOBAL_DATABASE_POSTGIS_SCHEMA_TEST")
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(url)
    connection = engine.connect()
    connection.execute(text(f"SET search_path TO {schema}"))
    yield connection
    connection.close()
    engine.dispose()


def execute_side_effect_default(connection):
    def _execute(query, params=None):
        return connection.execute(query, params or {})

    return with_rollback(connection, _execute)


def execute_query_side_effect_default(connection):
    def _execute_query(query, params=None):
        return connection.execute(text(query), params or {})

    return with_rollback(connection, _execute_query)


def call_procedure_side_effect_default(connection):
    def _call_procedure(procedure_name, *params, is_function=False):
        param_placeholders = ", ".join([f":p{i}" for i in range(len(params))])
        param_dict = {f"p{i}": params[i] for i in range(len(params))}
        if is_function:
            result = connection.execute(text(f"SELECT {procedure_name}({param_placeholders})"), param_dict)
            return result.fetchall()
        else:
            connection.execute(text(f"CALL {procedure_name}({param_placeholders})"), param_dict)
            return []

    return with_rollback(connection, _call_procedure)


def execute_multiple_queries_side_effect_default(connection):
    def _execute_multiple_queries(queries_with_params):
        for query, params in queries_with_params:
            connection.execute(text(query), params)

    return with_rollback(connection, _execute_multiple_queries)


def insert_query_commit_side_effect_default(connection):
    def _insert_query_commit(sql_queries, table_name, schema_name, df):
        for query in sql_queries:
            connection.execute(text(query))
        if df is not None:
            df.to_sql(name=table_name, schema=schema_name, con=connection, index=False, if_exists="append")

    return with_rollback(connection, _insert_query_commit)


def with_rollback(connection, func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            connection.rollback()
            connection.begin()
            raise

    return wrapped
