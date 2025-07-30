import logging
import re
import time
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Iterator, Sequence, Union
from contextlib import AbstractContextManager

import pandas as pd
from iotdb import SessionPool
from iotdb.Session import Session
from iotdb.SessionPool import create_session_pool, PoolConfig

from gxkit_dbtools.client.base import BaseDBClient
from gxkit_dbtools.exception import DBConnectionError, SQLExecutionError
from gxkit_dbtools.parser.sql_parser import SQLParser

try:
    from iotdb.utils.exception import IoTDBConnectionException
except ImportError:
    try:
        from iotdb.utils.IoTDBConnectionException import IoTDBConnectionException
    except ImportError:
        raise ImportError(
            "[IoTDBClient] Failed to import IoTDBConnectionException. Please ensure you have installed a compatible version of apache-iotdb"
        )


class StreamSessionManager(AbstractContextManager):
    def __init__(self, generator: Iterator[pd.DataFrame], session, return_fn):
        self._gen = generator
        self._session = session
        self._return_fn = return_fn
        self._closed = False

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self._gen)
        except StopIteration:
            self.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def close(self):
        if not self._closed:
            try:
                if hasattr(self._gen, "close"):
                    self._gen.close()
            finally:
                self._return_fn(self._session)
                self._closed = True

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


class BaseClient(BaseDBClient):
    """
    BaseClient - IoTDB 基础客户端
    Version: 0.1.2
    """

    def __init__(self, **connection_params):
        self.db_type = "iotdb"
        self._connection_params = connection_params

    def connect(self, *args, **kwargs):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def _get_session(self):
        raise NotImplementedError

    def _return_session(self, session):
        pass

    def execute(self, sql: str, auto_decision: bool = False, stream: bool = False,
                batch_size: Optional[int] = 10000, prefix_path: int = 1, max_retry: int = 3) -> Union[
        pd.DataFrame, Iterator[pd.DataFrame], int, None]:
        raise NotImplementedError

    def executemany(self, sqls: Sequence[str], auto_decision: bool = False, stream: bool = False,
                    batch_size: Optional[int] = 10000, collect_results: bool = True,
                    prefix_path: int = 1, max_retry: int = 3) -> List[Union[pd.DataFrame, int, None]]:
        if not isinstance(sqls, Sequence) or isinstance(sqls, str) or not sqls:
            raise SQLExecutionError("dbtools.IoTDBClient.executemany", str(sqls), "unsupported sqls type")
        results: List[Union[pd.DataFrame, int, None]] = []
        for sql in sqls:
            parsed_sql = SQLParser(sql, db_type="iotdb")
            sql_type = parsed_sql.sql_type()
            result = self.execute(sql, auto_decision=auto_decision, stream=stream, batch_size=batch_size,
                                  prefix_path=prefix_path, max_retry=max_retry)
            if collect_results and sql_type == "query":
                results.append(result)
        return results if collect_results else []

    def _stream_core(self, session, parsed_sql: SQLParser, batch_size: int, prefix_path: int, max_retry: int,
                     threshold: int = 48, col_time: str = "Time") -> Optional[Iterator[pd.DataFrame]]:
        def _generator_with_retry():
            nonlocal session
            last_error = None
            for attempt in range(1, max_retry + 1):
                try:
                    page_gen = self._page_generator(
                        session, parsed_sql, prefix_path, max_retry, batch_size, threshold, col_time
                    )
                    for df in page_gen:
                        yield df
                    return
                except IoTDBConnectionException as e:
                    last_error = e
                    logging.warning(
                        f"[IoTDBClient._stream_core] Retry {attempt}/{max_retry} after IoTDBConnectionException: {e}")
                    try:
                        self.close()
                    finally:
                        self.connect(**self._connection_params)
                    session = self._get_session()
                    time.sleep(attempt)
                except Exception:
                    raise
            raise SQLExecutionError("dbtools.IoTDBClient._stream_core", parsed_sql.sql(),
                                    f"Failed after {max_retry} retries: {last_error}")

        generator = _generator_with_retry()
        try:
            first_batch = next(generator)
        except StopIteration:
            self._return_session(session)
            return None
        except Exception:
            self._return_session(session)
            raise

        def stream_generator():
            try:
                yield first_batch
                yield from generator
            finally:
                self._return_session(session)

        return StreamSessionManager(stream_generator(), session, self._return_session)

    def _execute_with_retry(self, session, parsed_sql: SQLParser, prefix_path: int, max_retry: int,
                            threshold: int = 48, col_time: str = "Time") -> Optional[pd.DataFrame]:
        for attempt in range(1, max_retry + 1):
            try:
                dfs = list(self._page_generator(
                    session, parsed_sql, prefix_path, max_retry, None, threshold, col_time))
                if not dfs:
                    return None
                return pd.concat(dfs, ignore_index=True).drop_duplicates(subset="timestamp")
            except IoTDBConnectionException as e:
                logging.warning(
                    f"[IoTDBClient._execute_with_retry] Retry {attempt}/{max_retry} after IoTDBConnectionException: {e}")
                try:
                    self.close()
                finally:
                    self.connect(**self._connection_params)
                time.sleep(attempt)
            except Exception as e:
                raise SQLExecutionError("dbtools.IoTDBClient._execute_with_retry", parsed_sql.sql(), str(e)) from e
        raise SQLExecutionError("dbtools.IoTDBClient._execute_with_retry", parsed_sql.sql(),
                                f"Failed after {max_retry} retries")

    def _page_generator(self, session, parsed_sql: SQLParser, prefix_path: int, max_retry: int,
                        batch_size: Optional[int], threshold: int, col_time: str) -> Iterator[pd.DataFrame]:
        row_count = self._count_rows(session, parsed_sql, max_retry, default=0)
        seg_where = parsed_sql.segments("where").get("where")
        original_where = seg_where[0] if seg_where else None

        order_seg = parsed_sql.segments("order").get("order")
        order_sql = order_seg[0].strip() if order_seg else ""
        order_sql = re.sub(r"(?i)^order\s+by\s+", "", order_sql).strip()
        time_order_pattern = rf"(?i)^\b{col_time}\b(?:\s+(asc|desc))?$"
        direction = "asc"
        items = [item.strip() for item in order_sql.split(",")] if order_sql else []
        found = False
        for it in items:
            match = re.fullmatch(time_order_pattern, it)
            if match:
                direction = match.group(1).lower() if match.group(1) else "asc"
                found = True
                break
        if not items:
            items.append(f"{col_time} ASC")
            parsed_sql = SQLParser(parsed_sql.change_segments({"order": ", ".join(items)}), db_type="iotdb")
        elif not found:
            items.append(f"{col_time} ASC")
            parsed_sql = SQLParser(parsed_sql.change_segments({"order": ", ".join(items)}), db_type="iotdb")

        replacements = {}
        if batch_size:
            replacements["limit"] = str(batch_size)
        page_sql = SQLParser(parsed_sql.change_segments(replacements), db_type="iotdb") if replacements else parsed_sql

        retry = 0
        fetched = 0
        while True:
            df = self._execute_core(session, page_sql.sql(), "query", prefix_path, max_retry)
            if df is None or df.empty:
                if abs(fetched - row_count) > threshold and retry < max_retry:
                    retry += 1
                    time.sleep(retry)
                    continue
                break

            yield df
            fetched += df.shape[0]
            retry = 0

            if batch_size and df.shape[0] < batch_size:
                break
            if abs(fetched - row_count) <= threshold:
                break

            ts_extreme = df["timestamp"].max() if direction == "asc" else df["timestamp"].min()
            if pd.isnull(ts_extreme):
                break
            ts_next = int(ts_extreme) + 1 if direction == "asc" else int(ts_extreme) - 1
            cond = f"{col_time} {'>' if direction == 'asc' else '<'} {ts_next}"
            if original_where:
                time_pattern = rf"(?i)\b{col_time}\s*(>=|>|<=|<)\s*(\d+(?:\.\d+)?|'[^']+'|\"[^\"]+\")"
                if re.search(time_pattern, original_where):
                    final_where = re.sub(time_pattern, cond, original_where, count=1)
                else:
                    final_where = f"({original_where}) AND {cond}"
            else:
                final_where = cond

            replacements = {"where": final_where}
            if batch_size:
                replacements["limit"] = str(batch_size)
            page_sql = SQLParser(parsed_sql.change_segments(replacements), db_type="iotdb")
            row_count = self._count_rows(session, page_sql, max_retry, default=0)

    def _auto_decision(self, session, parsed_sql: SQLParser, max_retry: int, limit: int = 10000) -> bool:
        sql_type = parsed_sql.sql_type()
        operation = parsed_sql.operation()
        if sql_type != "query" or operation not in {"select", "union", "intersect", "except", "with"}:
            return False
        try:
            return self._count_rows(session, parsed_sql, max_retry, default=0) > limit
        except Exception:
            return False

    def _count_rows(self, session, parsed_sql: SQLParser, max_retry: int, default: Optional[int] = None) -> int:
        limit = parsed_sql.segments("limit").get("limit")
        count_limit = None if not limit else int(limit[0].split()[1])
        try:
            count_sql = SQLParser(parsed_sql.change_columns("count(*)"), db_type="iotdb").sql()
        except Exception:
            inner_sql = parsed_sql.sql()
            count_sql = f"SELECT count(*) FROM ({inner_sql})"
        try:
            count_df = self._execute_core(session, count_sql, "query", 1, max_retry)
            count_rows = 0 if count_df is None or count_df.empty else count_df.max().max()
            return min(count_limit, count_rows) if count_limit else count_rows
        except Exception as e:
            logging.error(f"[IoTDBClient._count_rows] Failed to count rows: {e}")
            if default is not None:
                return default
            raise SQLExecutionError("dbtools.IoTDBClient._count_rows", count_sql, str(e)) from e

    def _execute_core(self, session, sql: str, sql_type: str, prefix_path: int,
                      max_retry: int) -> Union[pd.DataFrame, int, None]:
        last_error = None
        for attempt in range(1, max_retry + 1):
            try:
                return self._execute_basic(session, sql, sql_type, prefix_path)
            except IoTDBConnectionException as e:
                last_error = e
                logging.warning(
                    f"[IoTDBClient._execute_core] Retry {attempt}/{max_retry} after IoTDBConnectionException: {e}")
                try:
                    self.close()
                finally:
                    self.connect(**self._connection_params)
                session = self._get_session()
                time.sleep(attempt)
            except Exception as e:
                raise SQLExecutionError("dbtools.IoTDBClient._execute_core", sql, str(e)) from e
        raise SQLExecutionError("dbtools.IoTDBClient._execute_core", sql,
                                f"Failed after {max_retry} retries: {last_error}")

    def _execute_basic(self, session, sql: str, sql_type: str, prefix_path: int) -> Union[pd.DataFrame, int, None]:
        if sql_type != "query":
            session.execute_non_query_statement(sql)
            return 1
        result = session.execute_query_statement(sql)
        df = result.todf()
        result.close_operation_handle()
        if df is None or df.empty:
            return None
        df.columns = self._build_col_mapping(list(df.columns), prefix_path)
        return df

    @staticmethod
    def _build_col_mapping(raw_cols: List[str], prefix_path: int) -> List[str]:
        def shorten(col: str) -> str:
            if col.lower() == "time":
                return "timestamp"
            if "(" in col and ")" in col:
                start = col.index("(")
                end = col.rindex(")")
                inner = col[start + 1: end]
                if "." in inner:
                    inner_short = ".".join(inner.split(".")[-prefix_path:]) if prefix_path > 0 else inner
                    return f"{col[: start + 1]}{inner_short}{col[end:]}"
                return col
            parts = col.split(".")
            return ".".join(parts[-prefix_path:]) if prefix_path > 0 else col

        return [shorten(col) for col in raw_cols]


class IoTDBClient(BaseClient):
    """
    IoTDBClient - IoTDB 单线程客户端
    Version: 0.1.2
    """

    def __init__(self, host: str, port: int, user: str, password: str, **kwargs):
        super().__init__(host=host, port=port, user=user, password=password, **kwargs)
        self.session: Optional[Session] = None
        self._last_success_time: Optional[datetime] = None
        self._reconnect_delay: timedelta = timedelta(minutes=10)
        self.connect(host, port, user, password, **kwargs)

    def _check_and_reconnect(self):
        if self.session is None or self._last_success_time is None:
            return
        now = datetime.now()
        if now - self._last_success_time > self._reconnect_delay:
            try:
                logging.info("[dbtools.IoTDBClient] Reconnecting due to inactivity timeout")
                self.session.execute_query_statement("SHOW STORAGE GROUP").close_operation_handle()
                self._last_success_time = now
            except Exception:
                logging.warning("[dbtools.IoTDBClient] Ping failed, reconnecting from scratch...")
                try:
                    self.close()
                finally:
                    self.connect(**self._connection_params)
                self._last_success_time = datetime.now()

    def connect(self, host: str, port: int, user: str, password: str, **kwargs) -> None:
        try:
            self.session = Session(host, port, user, password, **kwargs)
            self.session.open(False)
            self.session.execute_query_statement("SHOW STORAGE GROUP").close_operation_handle()
            self._last_success_time = datetime.now()
        except Exception as e:
            raise DBConnectionError("dbtools.IoTDBClient.connect", "iotdb", str(e)) from e

    def _get_session(self):
        if self.session is None:
            raise DBConnectionError("dbtools.IoTDBClient.execute", "iotdb", "Database not connected")
        return self.session

    def _return_session(self, session):
        now = datetime.now()
        if self._last_success_time:
            logging.debug(
                f"[IoTDBClient._return_session] Idle for {(now - self._last_success_time).total_seconds():.1f}s"
            )
        self._last_success_time = now

    def execute(self, sql: str, auto_decision: bool = False, stream: bool = False,
                batch_size: Optional[int] = 10000, prefix_path: int = 1, max_retry: int = 3) -> Union[
        pd.DataFrame, Iterator[pd.DataFrame], int, None]:
        session = self._get_session()
        parsed_sql = SQLParser(sql, db_type="iotdb")
        sql_type = parsed_sql.sql_type()

        if sql_type == "statement" and stream:
            logging.warning(
                "[dbtools.IoTDBClient.execute] | Stream function unsupported for this SQL. Using normal execution."
            )
            stream = False

        try:
            self._check_and_reconnect()

            if auto_decision and sql_type == "query" and self._auto_decision(session, parsed_sql, max_retry):
                if stream:
                    result = self._stream_core(session, parsed_sql, batch_size, prefix_path, max_retry)
                    return result
                return self._execute_with_retry(session, parsed_sql, prefix_path, max_retry)

            if stream and sql_type == "query":
                return self._stream_core(session, parsed_sql, batch_size, prefix_path, max_retry)

            result = self._execute_core(session, sql, sql_type, prefix_path, max_retry)
            return result
        finally:
            if not (stream and sql_type == "query"):
                self._return_session(session)

    def close(self) -> None:
        if self.session:
            try:
                self.session.close()
            except Exception:
                pass
            self.session = None


class IoTDBPoolClient(BaseClient):
    """
    IoTDBClient - IoTDB 线程池客户端
    Version: 0.1.2
    """

    def __init__(self, host: str, port: int, user: str, password: str, max_pool_size: int = 10,
                 wait_timeout_in_ms: int = 3000, **kwargs):
        super().__init__(host=host, port=port, user=user, password=password, max_pool_size=max_pool_size,
                         wait_timeout_in_ms=wait_timeout_in_ms, **kwargs)
        self.pool: Optional[SessionPool] = None
        self.connect(host, port, user, password, max_pool_size, wait_timeout_in_ms, **kwargs)

    def connect(self, host: str, port: int, user: str, password: str, max_pool_size: int, wait_timeout_in_ms: int,
                retry: int = 3, **kwargs) -> None:
        try:
            config = PoolConfig(host=host, port=str(port), user_name=user, password=password, **kwargs)
            self.pool = create_session_pool(config, max_pool_size=max_pool_size, wait_timeout_in_ms=wait_timeout_in_ms)
            last_error = None
            for attempt in range(1, retry + 1):
                try:
                    session = self.pool.get_session()
                    try:
                        session.execute_query_statement("SHOW STORAGE GROUP").close_operation_handle()
                    finally:
                        self.pool.put_back(session)
                    return
                except Exception as e:
                    if type(e).__name__ == "IoTDBConnectionException":
                        last_error = e
                        if attempt < retry:
                            logging.warning(
                                f"[dbtools.IoTDBPoolClient.connect] Retry {attempt}/{retry} after IoTDBConnectionException: {e}"
                            )
                        else:
                            break
                    else:
                        raise DBConnectionError("dbtools.IoTDBPoolClient.connect", "iotdb", str(e)) from e
            raise DBConnectionError("dbtools.IoTDBPoolClient.connect", "iotdb", str(last_error)) from last_error
        except Exception as e:
            raise DBConnectionError("dbtools.IoTDBPoolClient.connect", "iotdb", str(e)) from e

    def _get_session(self):
        if self.pool is None:
            raise DBConnectionError("dbtools.IoTDBPoolClient.execute", "iotdb", "Database not connected")
        last_error = None
        for attempt in range(1, 4):
            try:
                return self.pool.get_session()
            except Exception as e:
                last_error = e
                logging.warning(
                    f"[IoTDBPoolClient._get_session] Retry {attempt}/3 after {type(e).__name__}: {e}"
                )
                time.sleep(0.5)
        raise DBConnectionError("dbtools.IoTDBPoolClient.execute", "iotdb", str(last_error)) from last_error

    def _return_session(self, session):
        if self.pool is None:
            return
        last_error = None
        for attempt in range(1, 4):
            try:
                self.pool.put_back(session)
                return
            except Exception as e:
                last_error = e
                logging.warning(
                    f"[dbtools.IoTDBPoolClient._return_session] Retry {attempt}/3 after {type(e).__name__}: {e}")
                time.sleep(0.5)
        logging.error(
            f"[dbtools.IoTDBPoolClient._return_session] Failed to return session after 3 retries: {last_error}")
        try:
            session.close()
            logging.info("[dbtools.IoTDBPoolClient._return_session] Force-closed unreturned session.")
        except Exception as close_error:
            logging.error(f"[dbtools.IoTDBPoolClient._return_session] Failed to force close session: {close_error}")

    def execute(self, sql: str, auto_decision: bool = False, stream: bool = False, batch_size: Optional[int] = 10000,
                prefix_path: int = 1, max_retry: int = 3) -> Union[pd.DataFrame, Iterator[pd.DataFrame], int, None]:
        session = self._get_session()
        parsed_sql = SQLParser(sql, db_type="iotdb")
        sql_type = parsed_sql.sql_type()

        if sql_type == "statement" and stream:
            logging.warning(
                "[dbtools.IoTDBPoolClient.execute] | Stream function unsupported for this SQL. Using normal execution.")
            stream = False

        try:
            if auto_decision and sql_type == "query" and self._auto_decision(session, parsed_sql, max_retry):
                if stream:
                    return self._stream_core(session, parsed_sql, batch_size, prefix_path, max_retry)
                return self._execute_with_retry(session, parsed_sql, prefix_path, max_retry)

            if stream and sql_type == "query":
                return self._stream_core(session, parsed_sql, batch_size, prefix_path, max_retry)

            result = self._execute_core(session, sql, sql_type, prefix_path, max_retry)
            return result
        finally:
            if not (stream and sql_type == "query"):
                self._return_session(session)

    def close(self) -> None:
        if self.pool:
            try:
                self.pool.close()
            except Exception:
                pass
            self.pool = None
