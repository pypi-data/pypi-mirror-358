from urllib.parse import urlparse, parse_qs
from sqlalchemy import create_engine, insert, func, text, inspect, Engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from typing import List, Iterable, Type, Optional, Union
import time
import logging
from sqlalchemy.dialects.mysql import insert

# 设置日志模块（支持 cxppython 回退到标准库 logging）
try:
    import cxppython as cc
    logger = cc.logging
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

# 替换过时的 declarative_base
class Base(DeclarativeBase):
    pass

class MysqlDB:
    __instance = None

    def __init__(self, mysql_config, singleton: bool = False):
        """
        初始化 MysqlDB 实例，支持单例和非单例模式。
        :param mysql_config: 数据库配置（字符串或字典，包含 user, password, host, port, database 等）
        :param singleton: 是否启用单例模式（默认 False）
        """
        if singleton:
            if MysqlDB.__instance is not None:
                raise Exception("Singleton instance already exists. Use MysqlDB.instance() or MysqlDB.create().")
            MysqlDB.__instance = self
        self.engine = self._create_engine(mysql_config)
        self.session_factory = sessionmaker(bind=self.engine)

    @staticmethod
    def create(mysql_config):
        """
        创建单例实例。
        :param mysql_config: 数据库配置
        """
        if MysqlDB.__instance is None:
            MysqlDB(mysql_config, singleton=True)
        return MysqlDB.__instance

    @staticmethod
    def instance():
        """
        获取单例实例。
        :return: 单例 MysqlDB 实例
        """
        if MysqlDB.__instance is None:
            raise Exception("Database instance not initialized. Call create() first.")
        return MysqlDB.__instance

    def _create_engine(self, mysql_config):
        """
        创建 SQLAlchemy 引擎。
        :param mysql_config: 数据库配置（字符串或字典）
        :return: SQLAlchemy 引擎
        """
        config_dict = {}
        echo = False
        pool_settings = {
            "pool_size": 50,
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 1800,
            "pool_pre_ping": True
        }

        if isinstance(mysql_config, str):
            parsed = urlparse(f"mysql://{mysql_config}")
            config_dict = {
                "user": parsed.username,
                "password": parsed.password,
                "host": parsed.hostname,
                "port": parsed.port or 3306,
                "database": parsed.path.lstrip("/")
            }
            query_params = parse_qs(parsed.query)
            if "echo" in query_params:
                echo = query_params["echo"][0].lower() == "true"
            for key in pool_settings:
                if key in query_params:
                    try:
                        pool_settings[key] = int(query_params[key][0])
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid value for {key}: {query_params[key][0]}, using default")
        else:
            config_dict = mysql_config
            echo = mysql_config.get("echo", False)
            for key in pool_settings:
                if key in mysql_config:
                    try:
                        pool_settings[key] = int(mysql_config[key])
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid value for {key}: {mysql_config[key]}, using default")

        return create_engine(
            'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(**config_dict),
            echo=echo,
            **pool_settings
        )

    def session(self) -> Session:
        """
        获取一个新的 SQLAlchemy 会话。
        :return: SQLAlchemy 会话
        """
        if not self._is_connection_valid():
            self._reconnect()
        return self.session_factory()

    def get_engine(self) -> Engine:
        """
        获取 SQLAlchemy 引擎。
        :return: SQLAlchemy 引擎
        """
        return self.engine

    def get_db_connection(self):
        """
        返回 SQLAlchemy 引擎的连接。
        :return: 数据库连接
        """
        if not self._is_connection_valid():
            self._reconnect()
        return self.engine.connect()

    def _is_connection_valid(self):
        """
        检查数据库连接是否有效。
        :return: 连接是否有效
        """
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                return True
        except (OperationalError, DatabaseError):
            return False

    def _reconnect(self):
        """
        重新连接数据库。
        """
        logger.warning("Reconnecting to database...")
        try:
            self.engine.dispose()
            config_dict = {
                "user": self.engine.url.username,
                "password": self.engine.url.password,
                "host": self.engine.url.host,
                "port": self.engine.url.port or 3306,
                "database": self.engine.url.database
            }
            self.engine = self._create_engine(config_dict)
            self.session_factory = sessionmaker(bind=self.engine)
            logger.info("Database reconnected successfully")
        except Exception as e:
            logger.error(f"Failed to reconnect to database: {e}")
            raise

    def add(self, value) -> Optional[Exception]:
        """
        添加单个对象到数据库。
        :param value: 要添加的对象
        :return: 异常（如果有）或 None
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.session() as session, session.begin():
                    session.add(value)
                return None
            except (OperationalError, DatabaseError) as err:
                if "MySQL server has gone away" in str(err) and attempt < max_retries - 1:
                    logger.warning(f"Connection lost, retrying {attempt + 1}/{max_retries}")
                    self._reconnect()
                    time.sleep(1)
                    continue
                logger.error(f"Failed to add object: {err}")
                return err
        return Exception("Failed to add value after retries")

    def bulk_save(self, objects: Iterable[object]) -> Optional[Exception]:
        """
        批量保存对象到数据库。
        :param objects: 要保存的对象列表
        :return: 异常（如果有）或 None
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.session() as session, session.begin():
                    session.bulk_save_objects(objects)
                return None
            except (OperationalError, DatabaseError) as err:
                if "MySQL server has gone away" in str(err) and attempt < max_retries - 1:
                    logger.warning(f"Connection lost, retrying {attempt + 1}/{max_retries}")
                    self._reconnect()
                    time.sleep(1)
                    continue
                logger.error(f"Failed to bulk save objects: {err}")
                return err
        return Exception("Failed to bulk save after retries")

    def test_connection(self) -> bool:
        """
        测试数据库连接。
        :return: 连接是否成功
        """
        try:
            with self.engine.connect() as connection:
                logger.info(f"Database connection successful: {self.engine.url}")
                return True
        except OperationalError as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def batch_insert_records(
        self,
        model: Type[Base],
        data: List[dict],
        batch_size: int = 50,
        ignore_existing: bool = True,
        commit_per_batch: bool = True,
        retries: int = 3,
        delay: float = 1.0
    ) -> int:
        """
        批量插入记录。
        :param model: SQLAlchemy 模型类
        :param data: 批量插入的数据（字典列表）
        :param batch_size: 每批次处理的数据量
        :param ignore_existing: 是否忽略已存在的记录
        :param commit_per_batch: 是否每批次提交事务
        :param retries: 重试次数
        :param delay: 重试延迟（秒）
        :return: 插入的记录数
        """
        total_inserted = 0
        with self.session() as session:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                stmt = insert(model).values(batch)
                if ignore_existing:
                    stmt = stmt.prefix_with("IGNORE")
                for attempt in range(retries):
                    try:
                        result = session.execute(stmt)
                        total_inserted += result.rowcount
                        if commit_per_batch:
                            session.commit()
                        break
                    except (OperationalError, DatabaseError, IntegrityError) as e:
                        if "MySQL server has gone away" in str(e) or "Deadlock found" in str(e):
                            if attempt < retries - 1:
                                logger.warning(f"Connection error at attempt {attempt + 1}/{retries}, delay: {delay}s")
                                self._reconnect()
                                time.sleep(delay)
                                continue
                        logger.error(f"Batch insert failed at index {i}: {e}")
                        raise
                else:
                    logger.error(f"Batch insert failed at index {i} after {retries} retries")
                    raise RuntimeError("Max retries reached due to persistent deadlock")
        return total_inserted

    def batch_replace_records(
        self,
        model: Type[Base],
        data: List[dict],
        update_fields: List[str],
        conflict_keys: Union[str, List[str]] = None,
        batch_size: int = 50,
        commit_per_batch: bool = True,
        retries_count: int = 3,
        lock_table: bool = False
    ) -> int:
        """
        批量替换记录，支持联合唯一索引的冲突检测。
        :param model: SQLAlchemy 模型类
        :param data: 批量插入的数据（字典列表）
        :param update_fields: 需要更新的字段列表
        :param conflict_keys: 冲突检测的字段（单一字段或字段列表，默认为主键）
        :param batch_size: 每批次处理的数据量
        :param commit_per_batch: 是否每批次提交事务
        :param retries_count: 死锁重试次数
        :param lock_table: 是否显式加表级锁（谨慎使用）
        :return: 受影响的记录数
        """
        table = model.__table__
        if conflict_keys is None:
            conflict_keys = [col.name for col in table.primary_key]
        if isinstance(conflict_keys, str):
            conflict_keys = [conflict_keys]

        # 验证 conflict_keys
        valid_keys = {col.name for col in table.primary_key} | {col.name for col in table.columns if col.unique}
        inspector = inspect(self.engine)
        unique_constraints = {
            constraint['name']: constraint['column_names']
            for constraint in inspector.get_unique_constraints(table.name)
        }
        unique_constraints.update(
            {idx.name: [col.name for col in idx.columns] for idx in table.indexes if idx.unique}
        )

        conflict_keys_set = set(conflict_keys)
        if not (conflict_keys_set.issubset(valid_keys) or any(
                conflict_keys_set == set(cols) for cols in unique_constraints.values()
        )):
            raise ValueError(
                f"'{conflict_keys}' must match a primary key or unique constraint. "
                f"Available: {valid_keys}, Unique constraints: {unique_constraints}"
            )

        total_changed = 0
        with self.session() as session:
            if lock_table:
                logger.warning("Using table-level write lock; this may cause performance issues in high-concurrency scenarios.")
                session.execute(text(f"LOCK TABLE {table.name} WRITE"))
            try:
                for i in range(0, len(data), batch_size):
                    retries = retries_count
                    while retries > 0:
                        try:
                            batch = data[i:i + batch_size]
                            stmt = insert(model).values(batch)
                            set_dict = {field: func.values(table.c[field]) for field in update_fields}
                            stmt = stmt.on_duplicate_key_update(**set_dict)
                            result = session.execute(stmt)
                            total_changed += len(batch)
                            if commit_per_batch:
                                session.commit()
                            break
                        except (OperationalError, DatabaseError, IntegrityError) as e:
                            if "MySQL server has gone away" in str(e) or e.orig.args[0] == 1213:
                                retries -= 1
                                logger.warning(f"Connection error at index {i}, retries left: {retries}")
                                self._reconnect()
                                time.sleep(0.1 * (retries_count - retries))
                                continue
                            logger.error(f"Batch replace failed at index {i}: {e}")
                            session.rollback()
                            raise
                        except Exception as e:
                            logger.error(f"Batch replace failed at index {i}: {e}")
                            session.rollback()
                            raise
                    else:
                        logger.error(f"Batch replace failed at index {i} after {retries_count} retries")
                        raise RuntimeError("Max retries reached due to persistent deadlock")
            finally:
                if lock_table:
                    session.execute(text("UNLOCK TABLES"))
        return total_changed

    def close(self):
        """
        清理资源，关闭引擎。
        """
        self.engine.dispose()
        if MysqlDB.__instance == self:
            MysqlDB.__instance = None
        logger.info("Database engine closed")

    # 静态方法，供单例模式调用
    @staticmethod
    def static_session() -> Session:
        """
        获取单例模式的会话。
        :return: SQLAlchemy 会话
        """
        return MysqlDB.instance().session_factory()

    @staticmethod
    def static_get_db_connection():
        """
        获取单例模式的数据库连接。
        :return: 数据库连接
        """
        return MysqlDB.instance().get_db_connection()

    @staticmethod
    def static_add(value) -> Optional[Exception]:
        """
        单例模式下添加单个对象。
        :param value: 要添加的对象
        :return: 异常（如果有）或 None
        """
        return MysqlDB.instance().add(value)

    @staticmethod
    def static_bulk_save(objects: Iterable[object]) -> Optional[Exception]:
        """
        单例模式下批量保存对象。
        :param objects: 要保存的对象列表
        :return: 异常（如果有）或 None
        """
        return MysqlDB.instance().bulk_save(objects)

    @staticmethod
    def static_test_connection() -> bool:
        """
        单例模式下测试数据库连接。
        :return: 连接是否成功
        """
        return MysqlDB.instance().test_connection()

    @staticmethod
    def static_batch_insert_records(
        model: Type[Base],
        data: List[dict],
        batch_size: int = 50,
        ignore_existing: bool = True,
        commit_per_batch: bool = True,
        retries: int = 3,
        delay: float = 1.0
    ) -> int:
        """
        单例模式下批量插入记录。
        """
        return MysqlDB.instance().batch_insert_records(
            model, data, batch_size, ignore_existing, commit_per_batch, retries, delay
        )

    @staticmethod
    def static_batch_replace_records(
        model: Type[Base],
        data: List[dict],
        update_fields: List[str],
        conflict_keys: Union[str, List[str]] = None,
        batch_size: int = 50,
        commit_per_batch: bool = True,
        retries_count: int = 3,
        lock_table: bool = False
    ) -> int:
        """
        单例模式下批量替换记录。
        """
        return MysqlDB.instance().batch_replace_records(
            model, data, update_fields, conflict_keys, batch_size, commit_per_batch, retries_count, lock_table
        )

    @staticmethod
    def static_close():
        """
        单例模式下关闭数据库连接。
        """
        MysqlDB.instance().close()