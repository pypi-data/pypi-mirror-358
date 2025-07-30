import logging
import os
import socket
from typing import Callable, Dict, Iterable, List, Optional, Type, TypeVar, Union
from urllib.parse import parse_qsl, urlparse

from delta import DeltaTable
from delta._typing import ColumnMapping, ExpressionOrColumn, OptionalExpressionOrColumn
import psycopg2
import psycopg2.extras
from pyspark.sql import DataFrame, Row, SparkSession
from pyspark.sql.types import StructType
from pyeqx.core.utils.common import build_path
import pymssql

from pyeqx.core.common import SPARK_S3_PATH_PREFIX
from pyeqx.core.configuration import Configuration
from pyeqx.core.enums import DataModuleType, DataType
from pyeqx.core.errors import (
    ModuleNotSupportedException,
    StorageNotSupportedException,
)
from pyeqx.core.models.module import DataModule
from pyeqx.core.models.module.properties import (
    ApiDataModuleProperties,
    DatabaseDataModuleProperties,
    DataModuleProperties,
    FileDataModuleProperties,
    StreamDataModuleProperties,
)
from pyeqx.core.models.storage import Data
from pyeqx.core.models.storage.properties import (
    ApiDataProperties,
    AzureAdlsGen2StorageDataProperties,
    DataProperties,
    MongoDataProperties,
    PostgreSqlDataProperties,
    MSSqlDataProperties,
    S3DataProperties,
    CassandraDataProperties,
    KafkaDataProperties,
)
from pyeqx.core.reader import OperationReader
from pyeqx.core.spark.common import build_options, create_dataframe, get_session
from pyeqx.core.writer import OperationWriter

T = TypeVar("T", bound=DataProperties)


class ParsedParameters:
    def __init__(
        self,
        props: DataModuleProperties,
        storage_props: DataProperties,
        path: str,
    ) -> None:
        self.props = props
        self.storage_props = storage_props
        self.path = path


class Operation:
    __logger: logging.Logger

    __config: Configuration

    __name: str

    __spark_session: SparkSession

    __storages: Dict[str, Data]

    __jupyter_hostname: str
    __jupyter_host_ip: str

    def __init__(
        self, name: str, config: Configuration, logger: logging.Logger
    ) -> None:
        self.__name = name

        self.__config = config
        self.__logger = logger

        self.__jupyter_hostname = socket.gethostname()
        self.__jupyter_host_ip = socket.gethostbyname(self.__jupyter_hostname)

        self.__storages = self.__config.app.storages

    def initialize_spark(
        self, packages: list, options: dict = {}, is_debug: bool = False
    ):
        """
        Initialize Spark session

        Args:
            packages (list): List of packages to include
            options (dict, optional): Additional spark options. Defaults to {}.
            is_debug (bool, optional): Debugging mode to print all spark options to console. Defaults to False.
        """
        config = build_options(
            host_ip=self.__jupyter_host_ip, config=self.__config, options=options
        )

        spark = get_session(
            self.__name,
            config,
            packages,
            options,
        )

        spark_context = spark.sparkContext
        spark_hadoop_version = (
            spark_context._gateway.jvm.org.apache.hadoop.util.VersionInfo.getVersion()  # type: ignore
        )

        self.__logger.debug(f"SparkContext: {spark_context}")
        self.__logger.debug(
            f"Hadoop version: {spark_hadoop_version}",
        )

        self.__spark_session = spark

        if is_debug:
            for k, v in sorted(
                spark.sparkContext.getConf().getAll(), key=lambda item: item[0]
            ):
                self.__logger.debug(f"{k} = {v}")

        self.__reader = OperationReader(spark_session=spark, logger=self.__logger)
        self.__writer = OperationWriter(logger=self.__logger)

    def get_current_spark_session(self) -> SparkSession:
        return self.__spark_session

    def get_name(self) -> str:
        return self.__name

    def get_logger(self) -> logging.Logger:
        return self.__logger

    def print_debug_vars(self):
        self.__logger.info("jupyter hostname: " + self.__jupyter_hostname)
        self.__logger.info("jupyter ip: " + self.__jupyter_host_ip)

        self.__logger.info("**************** [Engine] ****************")

        if self.__config.engine.is_dedicated_spark:
            self.__logger.info(
                "spark master endpoint: " + self.__config.engine.spark_endpoint
            )

        self.__logger.info("**************** [Storage] ****************")
        engine_storage = self.__config.app.storages.get("system")
        if engine_storage.type == DataType.S3:
            engine_storage_props = self.__config.app.storages.get(
                "system"
            ).get_properties(S3DataProperties)

            obj_storage_endpoint = engine_storage_props.endpoint
            obj_storage_bucket_name = engine_storage_props.bucket_name

            self.__logger.info("engine storage endpoint: " + obj_storage_endpoint)
            self.__logger.info("engine storage bucket name: " + obj_storage_bucket_name)
        elif engine_storage.type == DataType.AzureAdlsGen2Storage:
            engine_storage_props = self.__config.app.storages.get(
                "system"
            ).get_properties(AzureAdlsGen2StorageDataProperties)

            obj_storage_endpoint = engine_storage_props.endpoint

            self.__logger.info("engine storage endpoint: " + obj_storage_endpoint)
            self.__logger.info("engine storage path: " + engine_storage_props.path)

        self.__logger.info("**************** [App] ****************")
        self.__logger.info("app name: " + self.__name)

    def upsert_delta_to(
        self,
        data: DataFrame,
        path: str,
        matches: Callable[[DataFrame], ColumnMapping],
        condition: Callable[[DataFrame], ExpressionOrColumn],
        alias: str = "datas",
    ) -> None:
        self.__create_delta_table_if_not_exists(path=path, scheme=data.schema)

        dt = DeltaTable.forPath(self.__spark_session, path)
        dt.alias(alias).merge(data, condition(data)).whenMatchedUpdate(
            set=matches(data)
        ).whenNotMatchedInsertAll().execute()

    def update_delta_to(
        self,
        data: DataFrame,
        path: str,
        condition: Callable[[DataFrame], ExpressionOrColumn],
        set: Callable[[DataFrame], ColumnMapping],
        alias: str = "datas",
    ):
        self.__create_delta_table_if_not_exists(path=path, scheme=data.schema)

        dt = DeltaTable.forPath(self.__spark_session, path)
        dt.alias(alias).update(
            condition=condition(data),
            set=set(data),
        )

    def upsert_to_postgresql(
        self,
        table: str,
        keys: list[str],
        data: DataFrame,
        storage_props: PostgreSqlDataProperties,
        page_size: int = 10240,
        is_rollback_on_error: Optional[bool] = True,
    ):
        """
        Upsert data to PostgreSql

        Args:
            table (str): Table name
            keys (list[str]): List of keys. Use in 'ON CONFLICT' clause.
            data (DataFrame): Dataframe to upsert
            storage_props (PostgreSqlDataProperties): PostgreSql storage properties
            page_size (int, optional): Page size. Defaults to 10240.
            is_rollback_on_error (Optional[bool], optional): Rollback transaction on error. Defaults to True.
        """

        try:
            self.__logger.debug(f"upsert data into PostgreSql, table: {table}.")

            parsed_url = urlparse(storage_props.url)
            query_params = dict(parse_qsl(parsed_url.query))
            parsed_path = urlparse(parsed_url.path)
            db = storage_props.db

            columns = data.columns
            columns_query = ", ".join(columns)
            on_conflict_query = ", ".join(keys)
            set_query = ", ".join([f"{key} = EXCLUDED.{key}" for key in columns])

            query = f"""
                INSERT INTO {table} ({columns_query})
                VALUES %s
                ON CONFLICT ({on_conflict_query}) DO UPDATE
                SET {set_query};
            """

            partition_counts = int(data.count() / page_size) + 1
            repartitioned_data = data.repartition(partition_counts)

            def execute_upsert(partition: Iterable[Row]):
                try:
                    connection = psycopg2.connect(
                        database=db,
                        host=parsed_path.netloc,
                        user=query_params.get("user"),
                        password=query_params.get("password"),
                        port="5432",
                    )

                    with connection.cursor() as cursor:
                        data_to_upsert = [
                            tuple(row[key] for key in columns) for row in partition
                        ]
                        psycopg2.extras.execute_values(cursor, query, data_to_upsert)
                        connection.commit()

                    cursor.close()
                    connection.close()
                except Exception as inner_e:
                    inner_error_message = (
                        f"error upsert into PostgreSql, table: {table}."
                    )

                    if is_rollback_on_error:
                        inner_error_message += " (rollback)"

                        if connection:
                            connection.rollback()

                    if connection:
                        connection.close()
                    raise Exception(inner_error_message) from inner_e

            repartitioned_data.rdd.foreachPartition(execute_upsert)
        except Exception as e:
            self.__logger.error(e, exc_info=True)

    def upsert_to_mssql(
        self,
        table: str,
        keys: list[str],
        data: DataFrame,
        storage_props: MSSqlDataProperties,
        page_size: int = 10240,
        is_rollback_on_error: Optional[bool] = True,
    ):
        """
        Upsert data to Azure SQL

        Args:
            table (str): Table name
            keys (list[str]): List of keys. Use in 'ON CONFLICT' clause.
            data (DataFrame): Dataframe to upsert
            storage_props (MSSqlDataProperties): Storage properties
            page_size (int, optional): Page size. Defaults to 10240.
            is_rollback_on_error (Optional[bool], optional): Rollback on error. Defaults to True.
        """

        try:
            self.__logger.debug(f"upsert data into Azure SQL, table: {table}.")

            parsed_url = urlparse(storage_props.url)
            parsed_path = urlparse(parsed_url.path)

            splits = parsed_path.netloc.split(";")
            hostname = parsed_path.hostname
            port = splits[0].split(":")[1]

            columns = data.columns

            source_values = ", ".join(["%s"] * len(columns))
            update_clauses = ", ".join([f"{col} = source.{col}" for col in columns])
            insert_columns = ", ".join(columns)
            insert_values = ", ".join([f"source.{col}" for col in columns])

            on_clauses = " AND ".join([f"target.{key} = source.{key}" for key in keys])

            query = f"""
                MERGE INTO {table} AS target
                USING (VALUES ({source_values})) AS source ({', '.join(columns)})
                ON {on_clauses}
                WHEN MATCHED THEN
                    UPDATE SET {update_clauses}
                WHEN NOT MATCHED THEN
                    INSERT ({insert_columns}) VALUES ({insert_values});
            """

            partition_counts = int(data.count() / page_size) + 1
            repartitioned_data = data.repartition(partition_counts)

            def execute_upsert(partition: Iterable[Row]):
                try:
                    parameters = dict(parse_qsl(parsed_path.netloc, separator=";"))

                    connection = pymssql.connect(
                        server=f"{hostname}:{port}",
                        user=parameters.get("user"),
                        password=parameters.get("password"),
                        database=parameters.get("database"),
                    )

                    with connection.cursor() as cursor:
                        data_to_upsert = [
                            tuple(row[key] for key in columns) for row in partition
                        ]
                        cursor.executemany(
                            query,
                            data_to_upsert,
                        )
                        connection.commit()

                    cursor.close()
                    connection.close()
                except Exception as inner_e:
                    inner_error_message = (
                        f"error upsert into Azure SQL, table: {table}."
                    )

                    if is_rollback_on_error:
                        inner_error_message += " (rollback)"

                        if connection:
                            connection.rollback()

                    if connection:
                        connection.close()
                    raise Exception(inner_error_message) from inner_e

            repartitioned_data.rdd.foreachPartition(execute_upsert)
        except Exception as e:
            self.__logger.error(e, exc_info=True)

    def read_source(
        self,
        data_module: DataModule,
        schema: Optional[StructType] = None,
        options: dict = {},
    ):
        try:
            self.__logger.debug("read source: started.")

            if data_module.type == DataModuleType.Api:
                data = self._read_source_from_api(
                    schema=schema,
                    data_module=data_module,
                    options=options,
                )

            elif data_module.type == DataModuleType.Database:
                data = self._read_source_from_database(
                    schema=schema,
                    data_module=data_module,
                    options=options,
                )
            elif data_module.type == DataModuleType.File:
                data = self._read_source_from_file(
                    schema=schema,
                    data_module=data_module,
                    options=options,
                )
            else:
                raise ModuleNotSupportedException(module=data_module)

            self.__logger.debug("read source: completed.")
            return data
        except Exception as e:
            self.__logger.error(f"read source failed: {e}")
            raise

    def write_destination(
        self,
        data: DataFrame,
        data_module: DataModule,
        options: dict = {},
        partition_by: Optional[Union[str, List[str]]] = None,
    ):
        try:
            self.__logger.debug("write destination: started.")

            if data_module.type == DataModuleType.Database:
                self._write_database(
                    data=data, data_module=data_module, options=options
                )
            elif data_module.type == DataModuleType.File:
                self._write_file(
                    data=data,
                    data_module=data_module,
                    options=options,
                    partition_by=partition_by,
                )
            elif data_module.type == DataModuleType.Stream:
                self._write_stream(data=data, data_module=data_module, options=options)
            else:
                raise ModuleNotSupportedException(module=data_module)

            self.__logger.debug("write destination: completed.")
        except Exception as e:
            self.__logger.error(f"write destination: failed: {e}")
            raise

    def _write_database(
        self, data: DataFrame, data_module: DataModule, options: dict = {}
    ):
        """
        Write data to database storage

        Args:
            data (DataFrame): data to write
            data_module (DataModule): data module
            options (dict, optional): additional options. Defaults to {}.
        """
        props = data_module.get_properties(DatabaseDataModuleProperties)
        storage = self.get_storage(name=props.storage)

        modes = ["append", "overwrite"]

        raw_mode = options.get("mode")
        parsed_mode = (
            raw_mode.lower()
            if raw_mode is not None and isinstance(raw_mode, str)
            else "append"
        )
        actual_mode = parsed_mode if parsed_mode in modes else "append"

        if storage.type == DataType.MSSql:
            storage_props = storage.get_properties(MSSqlDataProperties)
            self.__writer.write_to_mssql(
                data=data,
                mode=actual_mode,
                url=storage_props.url,
                table=props.table,
                options=options,
            )
        elif storage.type == DataType.MongoDB:
            storage_props = storage.get_properties(MongoDataProperties)
            uri = storage_props.uri
            db = storage_props.db

            self.__writer.write_to_mongodb(
                data=data,
                mode=actual_mode,
                uri=uri,
                db=db,
                table=props.table,
                options=options,
            )
        elif storage.type == DataType.PostgreSql:
            storage_props = storage.get_properties(PostgreSqlDataProperties)
            self.__writer.write_to_postgresql(
                data=data,
                mode=actual_mode,
                url=storage_props.url,
                table=props.table,
                options=options,
            )
        else:
            raise ModuleNotSupportedException(module=data_module)

    def _write_file(
        self,
        data: DataFrame,
        data_module: DataModule,
        options: dict = {},
        partition_by: Optional[Union[str, List[str]]] = None,
    ):
        """
        Write data to file storage with DeltaLake format (ADSL Gen2, S3)

        Args:
            data (DataFrame): data to write
            data_module (DataModule): data module
            options (dict, optional): additional options. Defaults to {}.
        """
        props = data_module.get_properties(FileDataModuleProperties)
        storage = self.get_storage(name=props.storage)

        modes = ["append", "overwrite"]

        raw_mode = options.get("mode")
        parsed_mode = (
            raw_mode.lower()
            if raw_mode is not None and isinstance(raw_mode, str)
            else "append"
        )
        actual_mode = parsed_mode if parsed_mode in modes else "append"

        paths = []

        if storage.type == DataType.S3:
            storage_props = storage.get_properties(S3DataProperties)

            if props.path:
                paths.append(props.path)

            path = build_path(
                base_path=storage_props.bucket_name,
                paths=paths,
            )
            self.__writer.write_to_s3(
                data=data,
                mode=actual_mode,
                path=path,
                options=options,
                partition_by=partition_by,
            )
        elif storage.type == DataType.AzureAdlsGen2Storage:
            storage_props = storage.get_properties(AzureAdlsGen2StorageDataProperties)

            if storage_props.path:
                paths.append(storage_props.path)

            if props.path:
                paths.append(props.path)

            path = build_path(
                base_path=storage_props.endpoint,
                paths=paths,
            )
            self.__writer.write_to(
                data=data,
                format="delta",
                mode=actual_mode,
                path=path,
                options=options,
            )
        else:
            raise StorageNotSupportedException(storage=storage)

    def _write_stream(
        self, data: DataFrame, data_module: DataModule, options: dict = {}
    ):
        """
        Write data to stream (e.g. Kafka

        Args:
            data (DataFrame): data to write
            data_module (DataModule): data module
            options (dict, optional): additional options. Defaults to {}.
        """
        props = data_module.get_properties(StreamDataModuleProperties)
        storage = self.get_storage(name=props.storage)

        if storage.type == DataType.Kafka:
            storage_props = storage.get_properties(KafkaDataProperties)

            topic_name = (
                storage_props.topic
                if props.name == "" or props.name is None
                else props.name
            )

            actual_options = {
                "topic": topic_name,
                "kafka.bootstrap.servers": storage_props.bootstrap_servers,
            }
            actual_options.update(options)

            self.__writer.write_to_kafka(
                data=data, topic=props.name, options=actual_options
            )
        else:
            raise StorageNotSupportedException(storage=storage)

    def delete(self, condition: OptionalExpressionOrColumn, data_module: DataModule):
        """
        Delete data

        **still support only Delta table.
        """
        try:
            self.__logger.debug("delete: started.")

            if data_module.type == DataModuleType.Database:
                raise ModuleNotSupportedException(module=data_module)
            elif data_module.type == DataModuleType.File:
                parse_parameters = self.__build_file_storage_data_module_parameters(
                    data_module=data_module
                )
                dt = DeltaTable.forPath(self.__spark_session, parse_parameters.path)

                dt.delete(condition)

            else:
                raise ModuleNotSupportedException(module=data_module)

            self.__logger.debug("delete: completed.")
        except Exception as e:
            self.__logger.error(f"delete failed: {e}")
            raise

        dt = DeltaTable.forPath(self.__spark_session)

    def delete_mssql(self, table: str, url: str, filter: str):
        """
        Delete data from MSSQL or Azure SQL

        Args:
            table (str): Table name
            url (str): Connection string
            filter (str): Filter condition (where clause)

        **this could potentially risk of SQL injection in filter.
        """
        url_splits = url.split(";")

        for url_split in url_splits:
            if url_split.startswith("user="):
                user = url_split.split("=")[1]
            elif url_split.startswith("password="):
                password = url_split.split("=")[1]
            elif url_split.startswith("database="):
                database = url_split.split("=")[1]
            elif url_split.startswith("jdbc:sqlserver://"):
                server = url_split.split("//")[1].split(":")[0]

        try:
            connection = pymssql.connect(
                server=server,
                user=user,
                password=password,
                database=database,
            )

            query = f"DELETE FROM {table} WHERE {filter}"

            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
        except Exception as e:
            connection.rollback()
            self.__logger.error(f"error: {e}", exc_info=True)

    def get_engine_storage_path(self, path: str):
        storage = self.__storages.get("system")
        props = storage.get_properties(S3DataProperties)

        path_prefix = SPARK_S3_PATH_PREFIX

        return os.path.join(path_prefix, props.bucket_name, path)

    def get_storage(self, name: str) -> Data:
        return self.__storages.get(name)

    def get_storage_properties(self, name: str, cls: Optional[Type[T]] = None) -> T:
        return self.get_storage(name=name).get_properties(cls)

    def get_reader(self) -> OperationReader:
        """
        Get reader object (helper for read data)

        Returns:
            OperationReader: reader object
        """
        return self.__reader

    def get_writer(self) -> OperationWriter:
        """
        Get writer object (helper for write data)

        Returns:
            OperationWriter: writer object
        """
        return self.__writer

    def get_config(self) -> Configuration:
        return self.__config

    def _read_source_from_api(
        self,
        data_module: DataModule,
        schema: StructType = None,
        options: dict = {},
    ):
        props = data_module.get_properties(ApiDataModuleProperties)
        storage = self.get_storage(name=props.storage)

        if storage.type == DataType.Api:
            # override some props
            if "parameters" in options:
                props.parameters = options.get("parameters")

            if "body" in options:
                props.body = options.get("body")

            return self.__reader.read_from_api(
                schema=schema,
                data_props=props,
                storage_props=storage.get_properties(ApiDataProperties),
                success_handler=(
                    options.get("successHandler")
                    if "successHandler" in options
                    else None
                ),
                error_handler=(
                    options.get("errorHandler") if "errorHandler" in options else None
                ),
            )
        else:
            raise ModuleNotSupportedException(module=data_module)

    def _read_source_from_database(
        self,
        data_module: DataModule,
        schema: StructType = None,
        options: dict = {},
    ):
        props = data_module.get_properties(DatabaseDataModuleProperties)
        storage = self.get_storage(name=props.storage)

        if storage.type == DataType.MSSql:
            storage_props = storage.get_properties(MSSqlDataProperties)
            return self.__reader.read_from_mssql(
                schema=schema,
                table=props.table,
                storage_props=storage_props,
                options=options,
            )
        elif storage.type == DataType.MongoDB:
            storage_props = storage.get_properties(MongoDataProperties)
            return self.__reader.read_from_mongodb(
                schema=schema,
                table=props.table,
                storage_props=storage_props,
                options=options,
            )
        elif storage.type == DataType.PostgreSql:
            storage_props = storage.get_properties(PostgreSqlDataProperties)
            return self.__reader.read_from_postgresql(
                schema=schema,
                table=props.table,
                storage_props=storage_props,
                options=options,
            )
        elif storage.type == DataType.Cassandra:
            storage_props = storage.get_properties(CassandraDataProperties)
            return self.__reader.read_from_cassandra(
                storage_props=storage_props,
                table=props.table,
                options=options,
            )
        else:
            raise ModuleNotSupportedException(module=data_module)

    def _read_source_from_file(
        self,
        data_module: DataModule,
        schema: StructType = None,
        options: dict = {},
    ):
        props = data_module.get_properties(FileDataModuleProperties)
        storage = self.get_storage(name=props.storage)

        if storage.type == DataType.S3:
            storage_props = storage.get_properties(S3DataProperties)
            storage_path = build_path(
                base_path=storage_props.bucket_name,
                paths=[props.path],
            )
            path = f"{SPARK_S3_PATH_PREFIX}{storage_path}"
        elif storage.type == DataType.AzureAdlsGen2Storage:
            storage_props = storage.get_properties(AzureAdlsGen2StorageDataProperties)
            path = build_path(
                base_path=storage_props.endpoint,
                paths=[storage_props.path, props.path],
            )
        else:
            raise StorageNotSupportedException(storage=storage)

        return self.__reader.read_from(
            schema=schema,
            format=props.type,
            path=path,
            options=options,
        )

    def __create_delta_table_if_not_exists(self, path: str, scheme: StructType):
        is_dt = DeltaTable.isDeltaTable(self.__spark_session, path)

        if not is_dt:
            new_df = create_dataframe(spark=self.__spark_session, schema=scheme)
            self.__writer.write_to(
                data=new_df, format="delta", mode="append", path=path
            )
