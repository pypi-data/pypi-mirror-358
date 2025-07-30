import logging
from datetime import datetime, timedelta
from typing import Optional, List, Iterator, Sequence, Union, Tuple

import pandas as pd
from clickhouse_driver import Client

from gxkit_dbtools.parser.sql_parser import SQLParser
from gxkit_dbtools.client.base import BaseDBClient
from gxkit_dbtools.exception import DBConnectionError, SQLExecutionError


class ClickHouseClient(BaseDBClient):
    """
    ClickHouseClient - ClickHouse 原生客户端
    Version: 0.1.1
    """

    def __init__(self, host: str, port: int, user: str, password: str, database: str, **kwargs):
        self.client: Optional[Client] = None
        self.db_type: str = "clickhouse"
        self._last_success_time: Optional[datetime] = None
        self._reconnect_delay: timedelta = timedelta(minutes=10)
        self._connection_params = dict(host=host, port=port, user=user, password=password, database=database, **kwargs)
        self.connect()

    def connect(self) -> None:
        try:
            self.client = Client(**self._connection_params)
            self.client.execute("SELECT 1")
            self._last_success_time = datetime.now()
        except Exception as e:
            logging.error(f"Failed to connect to ClickHouse: {e}")
            raise DBConnectionError("dbtools.ClickHouseClient.connect", "clickhouse", str(e)) from e

    def execute(self, sql: str, stream: bool = False, batch_size: int = 10000, values: Optional[List[Tuple]] = None) -> \
            Union[pd.DataFrame, Iterator[pd.DataFrame], int, None]:
        if self.client is None:
            raise DBConnectionError("dbtools.ClickHouseClient.execute", "clickhouse", "Not connected")

        sql = sql.strip()

        if values is not None:
            if not sql.lower().endswith("values"):
                raise SQLExecutionError("dbtools.ClickHouseClient.execute", sql,
                                        "'values' mode requires SQL to end with 'VALUES'")

            fake_sql = f"{sql} (null)"
            try:
                fake_parser = SQLParser(fake_sql, db_type="clickhouse")
                sql_type = fake_parser.sql_type()
                if sql_type != "statement":
                    raise SQLExecutionError("dbtools.ClickHouseClient.execute", sql,
                                            f"'values' mode only supports statement SQL, but got sql_type={sql_type}")

            except Exception as e:
                raise SQLExecutionError("dbtools.ClickHouseClient.execute", sql,
                                        f"SQLParser failed on values-mode SQL: {e}") from e

            if stream:
                logging.warning("[dbtools.ClickHouseClient.execute] | 'stream' ignored when 'values' is provided.")

            return self._execute_core(sql, sql_type, values=values)

        parsed_sql = SQLParser(sql, db_type="clickhouse")
        sql_type = parsed_sql.sql_type()
        operation = parsed_sql.operation()

        if stream and sql_type == "statement":
            logging.warning("[dbtools.ClickHouseClient.execute] | Stream unsupported for statement SQL. Using default.")
            stream = False

        if stream and sql_type == "query":
            return self._stream_core(sql, operation, parsed_sql, batch_size)

        return self._execute_core(sql, sql_type)

    def executemany(self, sqls: Sequence[str], stream: bool = False, batch_size: int = 10000,
                    collect_results: bool = True, values: Optional[Union[List[Tuple], List[List[Tuple]]]] = None) -> \
            List[Union[pd.DataFrame, int, None]]:
        if isinstance(sqls, str):
            sqls = [sqls]
            if isinstance(values, list) and values and isinstance(values[0], tuple):
                values = [values]
            elif values is None:
                values = [None]
            elif not isinstance(values, list) or not isinstance(values[0], (tuple, list)):
                raise SQLExecutionError("ClickHouseClient.executemany", sqls[0], "'values' type invalid")

        if not sqls:
            raise SQLExecutionError("ClickHouseClient.executemany", str(sqls), "'sqls' must be a non-empty sequence")

        if values is not None and len(sqls) != len(values):
            raise SQLExecutionError("ClickHouseClient.executemany", str(sqls),
                                    "Length of 'sqls' and 'values' does not match")

        results = []
        try:
            for idx, sql in enumerate(sqls):
                parsed_sql = SQLParser(sql, db_type="clickhouse")
                sql_type = parsed_sql.sql_type()
                val = values[idx] if values else None
                result = self.execute(sql, stream=stream, batch_size=batch_size, values=val)
                if collect_results and sql_type == "query":
                    results.append(result)
            return results if collect_results else []
        except Exception as e:
            raise SQLExecutionError("dbtools.ClickHouseClient.executemany", "; ".join(sqls), str(e)) from e

    def close(self) -> None:
        if self.client:
            self.client.disconnect()
            self.client = None

    def _execute_core(self, sql: str, sql_type: str, values: Optional[List[Tuple]] = None) -> Union[
        pd.DataFrame, int, None]:
        self._check_and_reconnect()
        try:
            if sql_type == "query":
                result, meta = self.client.execute(sql, with_column_types=True)
                if not result:
                    return None
                columns = [col[0] for col in meta]

                return pd.DataFrame(result, columns=columns)
            elif values is not None:
                self.client.execute(sql, values)
                self._last_success_time = datetime.now()
                return len(values)
            else:
                self.client.execute(sql)
                self._last_success_time = datetime.now()
                return 1
        except Exception as e:
            raise SQLExecutionError("dbtools.ClickHouseClient._execute_core", sql, str(e)) from e

    def _stream_core(self, sql: str, operation: str, parsed_sql: SQLParser, batch_size: int) -> Optional[
        Iterator[pd.DataFrame]]:
        self._check_and_reconnect()
        try:
            columns = self._get_columns(operation, parsed_sql)
            if columns is None:
                return None
            iter_rows = self.client.execute_iter(sql)
            self._last_success_time = datetime.now()

            def generator():
                batch = []
                for row in iter_rows:
                    batch.append(row)
                    if len(batch) >= batch_size:
                        self._last_success_time = datetime.now()
                        yield pd.DataFrame(batch, columns=columns)
                        batch.clear()
                if batch:
                    self._last_success_time = datetime.now()
                    yield pd.DataFrame(batch, columns=columns)

            return generator()

        except Exception as e:
            raise SQLExecutionError("dbtools.ClickHouseClient._stream_core", sql, str(e)) from e

    def _get_columns(self, operation: str, parsed_sql: SQLParser) -> Optional[List[str]]:
        if operation == "select":
            column_sql = parsed_sql.change_segments({"limit": "10"})
            test, meta = self.client.execute(column_sql, with_column_types=True)
            return [col[0] for col in meta] if test else None
        else:
            return parsed_sql.columns(mode="alias")

    def _check_and_reconnect(self):
        if self.client is None or self._last_success_time is None:
            return

        now = datetime.now()
        if now - self._last_success_time > self._reconnect_delay:
            try:
                logging.info("[dbtools.ClickHouseClient] Reconnecting due to inactivity timeout")
                self.client.connection.ping()
                self._last_success_time = now
            except Exception:
                logging.warning("[dbtools.ClickHouseClient] Ping failed, reconnecting from scratch...")
                self.close()
                self.connect()
                self._last_success_time = datetime.now()
