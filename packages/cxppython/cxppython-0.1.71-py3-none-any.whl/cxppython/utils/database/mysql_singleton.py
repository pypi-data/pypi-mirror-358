import time
from typing import Iterable, List, Type, Any, Union
from urllib.parse import urlparse, parse_qs
from sqlalchemy import text, insert, create_engine, select, inspect
from sqlalchemy.exc import OperationalError, DatabaseError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import insert
import cxppython as cc

try:
    from sqlalchemy.orm import DeclarativeBase
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    DeclarativeBase = declarative_base()

class Base(DeclarativeBase):
    pass

# --- 步骤 3: 定义你的模型类型，用于类型提示 ---
# 现在所有的模型都继承自 Base，所以类型提示非常简单。
ModelType = Type[Base]

class MysqlDBSingleton:
    __instance = None

    def __init__(self, mysql_config):
        if MysqlDBSingleton.__instance is not None:
            raise Exception("This class is a singleton, use DB.create()")
        else:
            MysqlDBSingleton.__instance = self
        self.engine = self._create_engine(mysql_config)
        self.session_factory = sessionmaker(bind=self.engine)

    @staticmethod
    def create(mysql_config):
        if MysqlDBSingleton.__instance is None:
            MysqlDBSingleton.__instance = MysqlDBSingleton(mysql_config)

    @staticmethod
    def instance():
        if MysqlDBSingleton.__instance is None:
            raise Exception("Database instance not initialized. Call create() first.")
        return MysqlDBSingleton.__instance

    @staticmethod
    def session() -> Session:
        instance = MysqlDBSingleton.instance()
        # 检查连接是否有效，无效则重连
        if not instance._is_connection_valid():
            instance._reconnect()
        session = instance.session_factory
        return session()

    @staticmethod
    def get_db_connection():
        instance = MysqlDBSingleton.instance()
        if not instance._is_connection_valid():
            instance._reconnect()
        return instance.engine.connect()

    @staticmethod
    def add(value) -> Exception | None:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with MysqlDBSingleton.session() as session:
                    with session.begin():  # 开启一个事务，代码块结束时自动提交或回滚
                        session.add(value)
                return None
            except (OperationalError, DatabaseError) as err:
                if "MySQL server has gone away" in str(err) and attempt < max_retries - 1:
                    cc.logging.warning(f"Connection lost, retrying {attempt + 1}/{max_retries}")
                    MysqlDBSingleton.instance()._reconnect()
                    time.sleep(1)
                    continue
                return err
        return Exception("Failed to add value after retries")

    @staticmethod
    def bulk_save(objects: Iterable[object]) -> Exception | None:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with MysqlDBSingleton.session() as session, session.begin():
                    session.bulk_save_objects(objects)
                return None
            except (OperationalError, DatabaseError) as err:
                if "MySQL server has gone away" in str(err) and attempt < max_retries - 1:
                    cc.logging.warning(f"Connection lost, retrying {attempt + 1}/{max_retries}")
                    MysqlDBSingleton.instance()._reconnect()
                    time.sleep(1)
                    continue
                return err
        return Exception("Failed to bulk save after retries")

    @staticmethod
    def test_db_connection():
        try:
            # 尝试建立连接
            with MysqlDBSingleton.instance().engine.connect() as connection:
                cc.logging.success(f"Database connection successful! : {MysqlDBSingleton.instance().engine.url}")
                connection.commit()
                return True
        except OperationalError as e:
            cc.logging.error(f"Failed to connect to the database: {e}")
            return False

    @staticmethod
    def test_connection():
        MysqlDBSingleton.test_db_connection()

    def _create_engine(self, mysql_config):
        echo = False
        config_dict = {}
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
        else:
            config_dict = mysql_config
            if "echo" in mysql_config:
                echo = mysql_config["echo"]

        return create_engine(
            'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(**config_dict),
            pool_size=200,
            max_overflow=0,
            pool_recycle=3600,  # 连接回收时间，防止超时
            pool_pre_ping=True,  # 每次使用前检查连接
            echo=echo
        )

    def _is_connection_valid(self):
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                return True
        except (OperationalError, DatabaseError):
            return False

    def _reconnect(self):
        cc.logging.warning("Reconnecting to database...")
        try:
            self.engine.dispose()  # 释放旧连接
            config_dict = {
                "user": self.engine.url.username,
                "password": self.engine.url.password,
                "host": self.engine.url.host,
                "port": self.engine.url.port or 3306,
                "database": self.engine.url.database
            }
            self.engine = self._create_engine(config_dict)
            self.session_factory = sessionmaker(bind=self.engine)
            cc.logging.info("Database reconnected successfully")
        except Exception as e:
            cc.logging.error(f"Failed to reconnect to database: {e}")
            raise

    @staticmethod
    def batch_insert_records(session: Session,
                             model: Type[ModelType],
                             data: List,
                             batch_size: int = 50,
                             ignore_existing: bool = True,
                             commit_per_batch: bool = True,
                             retries=3,
                             delay=1):
        total_inserted = 0
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            stmt = insert(model).values(batch)
            if ignore_existing:
                stmt = stmt.prefix_with("IGNORE")
            for attempt in range(retries):
                try:
                    result = session.execute(stmt)
                    inserted_count = result.rowcount
                    total_inserted += inserted_count
                    break
                except (OperationalError, DatabaseError) as e:
                    if "MySQL server has gone away" in str(e) or "Deadlock found" in str(e):
                        if attempt < retries - 1:
                            cc.logging.warning(f"Connection error at attempt {attempt + 1}/{retries}, delay:{delay}")
                            MysqlDBSingleton.instance()._reconnect()
                            time.sleep(delay)
                            continue
                    raise
            if commit_per_batch:
                session.commit()
        return total_inserted

    @staticmethod
    def batch_replace_records(
            session: Session,
            model: Type[ModelType],
            data: List[dict],
            update_fields: List[str],
            conflict_keys: str | List[str] = None,
            batch_size: int = 50,
            commit_per_batch: bool = True,
            retries_count: int = 3,
            lock_table: bool = False
    ) -> int | None | Any:
        """
        批量替换记录，支持联合唯一索引的冲突检测。

        :param session: SQLAlchemy 会话
        :param model: SQLAlchemy 模型类
        :param data: 批量插入的数据（字典列表）
        :param update_fields: 需要更新的字段列表（例如 ['predict_amount', 'backtest_score']）
        :param conflict_keys: 冲突检测的字段（单一字段 str 或字段列表 List[str]，例如 'id' 或 ['netuid', 'hotkey']），默认为主键
        :param batch_size: 每批次处理的数据量
        :param commit_per_batch: 是否每批次提交事务
        :param retries_count: 死锁重试次数
        :param lock_table: 是否显式加表级锁
        :return: 受影响的记录数
        """
        table = model.__table__

        # 如果未提供 conflict_keys，默认为主键
        if conflict_keys is None:
            conflict_keys = [col.name for col in table.primary_key]

        # 统一处理 conflict_keys 为列表
        if isinstance(conflict_keys, str):
            conflict_keys = [conflict_keys]

        # 验证 conflict_keys 是否有效（必须是主键或唯一约束中的字段）
        valid_keys = {col.name for col in table.primary_key} | {col.name for col in table.columns if col.unique}

        # 获取唯一约束（来自 UniqueConstraint）
        inspector = inspect(session.bind)
        unique_constraints = {
            constraint['name']: constraint['column_names']
            for constraint in inspector.get_unique_constraints(table.name)
        }

        # 获取唯一索引（来自 Index）
        unique_constraints.update(
            {idx.name: [col.name for col in idx.columns] for idx in table.indexes if idx.unique}
        )

        # unique_constraints = {idx.name: [col.name for col in idx.columns] for idx in table.indexes if idx.unique}

        # 检查 conflict_keys 是否匹配主键或唯一约束（包括联合索引）
        conflict_keys_set = set(conflict_keys)
        if conflict_keys_set.issubset(valid_keys) or any(
                conflict_keys_set == set(cols) for cols in unique_constraints.values()
        ):
            pass
        else:
            raise ValueError(
                f"'{conflict_keys}' must match a primary key or unique constraint. "
                f"Available: {valid_keys}, Unique constraints: {unique_constraints}"
            )

        total_changed = 0
        # 显式加表级锁
        if lock_table:
            session.execute(text(f"LOCK TABLE {table.name} WRITE"))

        try:
            for i in range(0, len(data), batch_size):
                retries = retries_count
                while retries > 0:
                    try:
                        batch = data[i:i + batch_size]
                        stmt = insert(model).values(batch)
                        # 构造 ON DUPLICATE KEY UPDATE 的更新字段
                        set_dict = {field: func.values(table.c[field]) for field in update_fields}
                        stmt = stmt.on_duplicate_key_update(**set_dict)
                        result = session.execute(stmt)
                        if result.rowcount > 0:
                            total_changed += len(batch)

                        if commit_per_batch:
                            session.commit()
                        break
                    except (OperationalError, DatabaseError) as e:
                        if "MySQL server has gone away" in str(e) or e.orig.args[0] == 1213:
                            retries -= 1
                            cc.logging.warning(f"Connection error at index {i}, retries left: {retries}")
                            MysqlDBSingleton.instance()._reconnect()
                            time.sleep(0.1 * (3 - retries))
                            session.rollback()
                            continue
                        cc.logging.error(f"Batch replace failed at index {i}: {e}")
                        session.rollback()
                        raise
                    except Exception as e:
                        cc.logging.error(f"Batch replace failed at index {i}: {e}")
                        session.rollback()
                        raise
                else:
                    cc.logging.error(f"Batch replace failed at index {i} after {retries} retries")
                    raise RuntimeError("Max retries reached due to persistent deadlock")
        finally:
            # 释放锁
            if lock_table:
                session.execute(text("UNLOCK TABLES"))

        return total_changed

    @staticmethod
    def close():
        """
        清理资源，关闭引擎。
        """
        if MysqlDBSingleton.__instance:
            MysqlDBSingleton.__instance.engine.dispose()
            MysqlDBSingleton.__instance = None