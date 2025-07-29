"""Database Library"""

# Column, Table, MetaData API
#     https://docs.sqlalchemy.org/en/14/core/metadata.html#column-table-metadata-api
# CursorResult
#     https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.CursorResult
# PostgreSQL 14 Data Types
#     https://www.postgresql.org/docs/14/datatype.html

import csv
import json
from datetime import date, datetime
from typing import Any, Type

import pandas as pd
from loguru import logger
from sqlalchemy import CursorResult, Engine, Index, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, declarative_base

from . import utils

Base = declarative_base()


def orm_object_to_dict(obj, include: list | None = None) -> dict | None:
    """
    将 ORM 对象转为 dict, 可选择只包含部分字段.
    :param obj: SQLAlchemy ORM 实例
    :param include: 要保留的字段列表(白名单)
    """
    if obj is None:
        return None

    data = {}

    for column in obj.__table__.columns:
        key = column.name
        if include and key not in include:
            continue
        value = getattr(obj, key)
        if isinstance(value, (datetime, date)):
            # data[key] = value.isoformat()
            data[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            data[key] = value

    return data


def orm_list_to_dict(obj_list, include: list | None = None) -> list:
    return [orm_object_to_dict(obj, include) for obj in obj_list]


def orm_to_dict(obj, include: list | None = None) -> dict | list | None:
    """
    ORM 对象 (单个或列表) 转 JSON 字符串.
    :param include: 仅导出指定字段（白名单）
    """
    try:
        if isinstance(obj, list):
            data = orm_list_to_dict(obj, include)
        else:
            data = orm_object_to_dict(obj, include)
        return data
    except Exception as e:
        logger.exception(e)
        return None


def build_raw_where_clause(data: dict) -> tuple[str, list] | None:
    """
    将字段数据转换为 SQL WHERE 条件(使用原生 SQL)
    支持字段后缀操作: __like, __gt, __lt, __ne, __in, __between
    返回值: SQL字符串和参数列表 (为了避免 SQL 注入风险, 不直接返回 SQL 语句)
    """

    try:

        sql_parts = []
        params = []

        for field, value in data.items():

            if "__" in field:

                base, op = field.split("__", 1)

                if op == "like":
                    sql_parts.append(f"{base} LIKE %s")
                    params.append(f"%{value}%")
                elif op == "gt":
                    sql_parts.append(f"{base} > %s")
                    params.append(value)
                elif op == "lt":
                    sql_parts.append(f"{base} < %s")
                    params.append(value)
                elif op == "ne":
                    sql_parts.append(f"{base} != %s")
                    params.append(value)
                elif op == "in" and isinstance(value, list):
                    placeholders = ", ".join(["%s"] * len(value))
                    sql_parts.append(f"{base} IN ({placeholders})")
                    params.extend(value)
                elif op == "between" and isinstance(value, list) and len(value) == 2:
                    sql_parts.append(f"{base} BETWEEN %s AND %s")
                    params.extend(value)

            else:

                sql_parts.append(f"{field} = %s")
                params.append(value)

        where_clause = " AND ".join(sql_parts)

        return where_clause, params

    except Exception as e:
        logger.exception(e)
        return None


# --------------------------------------------------------------------------------------------------


class Database:
    """Database"""

    engine = create_engine("sqlite://")

    def __init__(self, engine: Engine | None = None, target: str | None = None, **options):
        """Initiation"""
        if engine is not None:
            self.engine = engine
        elif isinstance(target, str) and utils.isTrue(target, str):
            if utils.isTrue(options, dict):
                self.engine = create_engine(target, **options)
            else:
                self.engine = create_engine(target)
        else:
            pass

    # ----------------------------------------------------------------------------------------------

    def initializer(self):
        """ensure the parent proc's database connections are not touched in the new connection pool"""
        self.engine.dispose(close=False)

    # ----------------------------------------------------------------------------------------------

    def connect_test(self) -> bool:
        info = "Database connect test"
        try:
            logger.info(f"{info} ......")
            with self.engine.connect() as _:
                logger.success(f"{info} [success]")
                return True
        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False

    # ----------------------------------------------------------------------------------------------

    def metadata_init(self, base: DeclarativeBase, **kwargs) -> bool:
        # https://stackoverflow.com/questions/19175311/how-to-create-only-one-table-with-sqlalchemy
        info = "Database init table"
        try:
            logger.info(f"{info} ......")
            base.metadata.drop_all(self.engine, **kwargs)
            base.metadata.create_all(self.engine, **kwargs)
            logger.success(f"{info} [success]")
            return True
        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False

    # ----------------------------------------------------------------------------------------------

    def initialization_table(self, table: str):
        """初始化表"""

        # 初始化所有表
        #   db.metadata_init(Base)
        # 初始化指定表
        #   database.metadata_init(Base, tables=[Base.metadata.tables['ashare']])
        self.metadata_init(Base, tables=[Base.metadata.tables[table]])

    # ----------------------------------------------------------------------------------------------

    def create_index(self, index_name, table_field) -> bool:
        # 创建索引
        #   https://stackoverflow.com/a/41254430
        # 示例:
        #   index_name: a_share_list_code_idx1
        #   table_field: Table_a_share_list.code
        info = "Database create index"
        try:
            logger.info(f"{info} ......")
            idx = Index(index_name, table_field)
            try:
                idx.drop(bind=self.engine)
            except Exception as e:
                logger.exception(e)
            idx.create(bind=self.engine)
            logger.success(f"{info} [success]")
            return True
        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.error(e)
            return False

    # ----------------------------------------------------------------------------------------------

    # 私有函数, 保存 execute 的结果到 CSV 文件
    def _result_save(self, file, data) -> bool:
        try:
            outcsv = csv.writer(file)
            outcsv.writerow(data.keys())
            outcsv.writerows(data)
            logger.success("save to csv success")
            return True
        except Exception as e:
            logger.error("save to csv failed")
            logger.exception(e)
            return False

    # ----------------------------------------------------------------------------------------------

    # def execute(
    #     self,
    #     sql: str | None = None,
    #     sql_file: str | None = None,
    #     sql_file_kwargs: dict | None = None,
    #     csv_file: str | None = None,
    #     csv_file_kwargs: dict | None = None
    # ) -> CursorResult[Any] | bool:
    #     """"运行"""

    #     # ------------------------------------------------------------

    #     # 提取 SQL
    #     # 如果 sql 和 sql_file 同时存在, 优先执行 sql

    #     sql_object = None

    #     info: str = f"""Extract SQL: {sql}"""

    #     try:

    #         logger.info(f"{info} ......")

    #         if utils.isTrue(sql, str):

    #             sql_object = sql

    #         elif sql_file is not None and utils.isTrue(sql_file, str):

    #             # 判断文件是否存在
    #             if isinstance(sql_file, str) and utils.check_file_type(sql_file, "file") is False:

    #                 logger.error(f"No such file: {sql_file}")
    #                 return False

    #             if isinstance(sql_file, str) and utils.isTrue(sql_file, str):

    #                 # 读取文件内容
    #                 if sql_file_kwargs is not None and utils.isTrue(sql_file_kwargs, dict):
    #                     with open(sql_file, "r", encoding="utf-8", **sql_file_kwargs) as _file:
    #                         sql_object = _file.read()
    #                 else:
    #                     with open(sql_file, "r", encoding="utf-8") as _file:
    #                         sql_object = _file.read()

    #         else:

    #             logger.error("SQL or SQL file error")
    #             logger.error(f"{info} [failed]")
    #             return False

    #         logger.success(f'{info} [success]')

    #     except Exception as e:

    #         logger.error(f"{info} [failed]")
    #         logger.exception(e)
    #         return False

    #     # ------------------------------------------------------------

    #     # 执行 SQL

    #     info = f"""Execute SQL: {sql_object}"""

    #     try:

    #         logger.info(f"{info} ......")

    #         with self.engine.connect() as connect:

    #             # 执行SQL
    #             if sql_object is None:
    #                 return False

    #             result = connect.execute(text(sql_object))

    #             connect.commit()

    #             if csv_file is None:
    #                 # 如果 csv_file 没有定义, 则直接返回结果
    #                 logger.success(f'{info} [success]')
    #                 return result

    #             # 如果 csv_file 有定义, 则保存结果到 csv_file
    #             info_of_save = f"Save result to file: {csv_file}"
    #             logger.info(f"{info_of_save} .......")

    #             # 保存结果
    #             if isinstance(csv_file_kwargs, dict) and utils.isTrue(csv_file_kwargs, dict):
    #                 with open(csv_file, "w", encoding="utf-8", **csv_file_kwargs) as _file:
    #                     result_of_save = self._result_save(_file, result)
    #             else:
    #                 with open(csv_file, "w", encoding="utf-8") as _file:
    #                     result_of_save = self._result_save(_file, result)

    #             # 检查保存结果
    #             if result_of_save is True:
    #                 logger.success(f'{info_of_save} [success]')
    #                 logger.success(f'{info} [success]')
    #                 return True

    #             logger.error(f"{info_of_save} [failed]")
    #             logger.error(f"{info} [failed]")
    #             return False

    #     except Exception as e:

    #         logger.error(f'{info} [failed]')
    #         logger.exception(e)
    #         return False

    # ----------------------------------------------------------------------------------------------

    def connect_execute(
        self,
        sql: str | None = None,
        read_sql_file: dict | None = None,
        save_to_csv: dict | None = None,
    ) -> CursorResult[Any] | bool | None:

        info: str = "Database connect execute"

        logger.info(f"{info} ......")

        sql_statement: str = ""

        # ------------------------------------------------------------------------------------------

        try:
            # SQL文件优先
            if isinstance(read_sql_file, dict) and utils.isTrue(read_sql_file, dict):
                read_sql_file.pop("encoding")
                read_sql_file_kwargs: dict = {
                    "mode": "r",
                    "encoding": "utf-8",
                    **read_sql_file,
                }
                with open(encoding="utf-8", **read_sql_file_kwargs) as _file:
                    sql_statement = _file.read()
            else:
                if not isinstance(sql, str):
                    return None
                sql_statement = sql
        except Exception as e:
            logger.exception(e)
            return None

        # ------------------------------------------------------------------------------------------

        # 创建一个连接
        with self.engine.connect() as connection:

            # 开始一个事务
            with connection.begin():  # 事务会自动提交或回滚

                try:

                    # 执行 SQL 查询
                    result = connection.execute(text(sql_statement))

                    # 执行成功
                    logger.success(f"{info} [success]")

                    # 返回查询结果
                    if isinstance(save_to_csv, dict) and utils.isTrue(save_to_csv, dict):
                        save_to_csv_kwargs: dict = {
                            "mode": "w",
                            "encoding": "utf-8",
                            **save_to_csv,
                        }
                        with open(encoding="utf-8", **save_to_csv_kwargs) as _file:
                            return self._result_save(_file, result)

                    return result

                except Exception as e:
                    # 发生异常时回滚事务
                    logger.info(f"{info} [failed]")
                    logger.exception(e)
                    return None

    # ----------------------------------------------------------------------------------------------

    def drop_table(self, table_name: str) -> bool:
        """删除表"""

        info: str = f"drop table: {table_name}"

        try:
            logger.info(f"{info} ......")
            self.connect_execute(sql=f"DROP TABLE IF EXISTS {table_name}")
            logger.success(f"{info} [success]")
            return True
        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False

    # ----------------------------------------------------------------------------------------------

    def read_with_pandas(self, method: str = "read_sql", result_type: str = "df", **kwargs) -> pd.DataFrame | list | dict:
        """读取数据"""

        # 使用SQL查询数据: 使用 pd.read_sql 的参数
        # read_data_with_pandas(by="sql", result_type="df", sql="SELECT * FROM table ORDER BY date DESC LIMIT 1")

        # 读取表中的数据: 使用 pd.read_sql_table 的参数
        # read_data_with_pandas(by="table", result_type="df", table_name="ashare")

        data: pd.DataFrame = pd.DataFrame()

        info: str = "read data"

        try:

            logger.info(f"{info} ......")

            # 从 kwargs 中删除 con 键
            kwargs.pop("con", None)

            match method:
                case "read_sql":
                    data = pd.read_sql(con=self.engine, **kwargs)
                case "read_sql_query":
                    data = pd.read_sql_query(con=self.engine, **kwargs)
                case "read_sql_table":
                    data = pd.read_sql_table(con=self.engine, **kwargs)
                case _:
                    logger.error(f"{info} [incorrect method: {method}]")
                    return data

            if data.empty:
                logger.error(f"{info} [failed]")
                return data

            logger.success(f"{info} [success]")

            match result_type:
                case "json":
                    return json.loads(data.to_json(orient="records"))
                case "dict":
                    return data.to_dict()
                case "list":
                    # https://stackoverflow.com/a/26716774
                    return data.to_dict("list")
                case _:
                    return data

        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return data

    # ----------------------------------------------------------------------------------------------

    def create_data(self, TS: Type, data: list) -> bool:
        """创建数据. TS: Table Schema"""

        info: str = "create data"

        if not utils.isTrue(data, list):
            logger.error(f"{info} [data type is not a list]")

        logger.info(f"{info} ......")

        with Session(self.engine) as session:

            try:

                for item in data:

                    if not utils.isTrue(item, dict):
                        logger.error(f"{info} [data type error]")
                        session.rollback()
                        return False

                    session.add(TS(**item))

                session.commit()

                logger.success(f"{info} [success]")

                return True

            except Exception as e:
                session.rollback()
                logger.error(f"{info} [failed]")
                logger.exception(e)
                return False
