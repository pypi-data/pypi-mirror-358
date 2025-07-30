from logging import Logger
from typing import Any, Callable
import requests
from urllib.parse import urljoin

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from pyeqx.core.models.module.properties import (
    ApiDataModuleProperties,
)
from pyeqx.core.models.storage.properties import (
    ApiDataProperties,
    CassandraDataProperties,
    MongoDataProperties,
    MSSqlDataProperties,
    PostgreSqlDataProperties,
    SqlDataProperties,
)
from pyeqx.core.spark.common import create_dataframe


class OperationReader:
    def __init__(self, spark_session: SparkSession, logger: Logger) -> None:
        self.__logger = logger
        self.__spark_session = spark_session

    def read_from_s3(
        self,
        path: str,
        format: str,
        schema: StructType = None,
        options: dict = {},
    ) -> DataFrame:
        """
        Read data from S3 (Amazon S3) storage (or any compatible storage)

        Args:
            path (str): path to read data (e.g. 'bucket-name/folder-name', 'bucket-name/folder-name/file.csv')
            format (str): format of data (e.g. 'csv', 'delta')
            schema (StructType, optional): schema of data. Defaults to None.
            options (dict, optional): additional options for reading data. Defaults to {}.

        Returns:
            DataFrame: _description_
        """

        if options is None:
            options = {}

        return self.read_from(schema=schema, path=path, format=format, options=options)

    def read_from_mongodb(
        self,
        table: str,
        storage_props: MongoDataProperties,
        schema: StructType = None,
        options: dict = None,
    ) -> DataFrame:
        """
        Read data from MongoDB storage

        Args:
            table (str): collection name
            storage_props (MongoDataProperties): MongoDB storage properties
            schema (StructType, optional): schema of data. Defaults to None.
            options (dict, optional): additional options for reading data. Defaults to None.

        Returns:
            DataFrame: data from MongoDB
        """

        if options is None:
            options = {}

        spark_options = {
            "spark.mongodb.connection.uri": storage_props.uri,
            "spark.mongodb.database": storage_props.db,
            "spark.mongodb.collection": table,
        }

        options.update(spark_options)

        return self.read_from(
            schema=schema, format="mongodb", options=options, path=table
        )

    def read_from_mssql(
        self,
        table: str,
        storage_props: MSSqlDataProperties,
        schema: StructType = None,
        options: dict = None,
    ) -> DataFrame:
        """
        Read data from MSSQL storage (Azure SQL Database, SQL Server, etc.)

        - using 'com.microsoft.sqlserver.jdbc.SQLServerDriver' as driver

        Args:
            table (str): table name
            storage_props (MSSqlDataProperties): MSSQL storage properties
            schema (StructType, optional): schema of data. Defaults to None.
            options (dict, optional): additional options for reading data. Defaults to None.

        Returns:
            DataFrame: data from MSSQL

        Notes:
            - change format back to 'jdbc' (default). To use 'com.microsoft.sqlserver.jdbc.spark',
              please use read_from_sql method instead and set format to 'com.microsoft.sqlserver.jdbc.spark'
            - schema is required with entire table column names and types, otherwise, it will be inferred from the data
        """

        if options is None:
            options = {}

        spark_options = {
            "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        }

        options.update(spark_options)

        return self.read_from_sql(
            schema=schema,
            table=table,
            storage_props=storage_props,
            options=options,
        )

    def read_from_postgresql(
        self,
        table: str,
        storage_props: PostgreSqlDataProperties,
        schema: StructType = None,
        options: dict = None,
    ) -> DataFrame:
        """
        Read data from PostgreSQL storage

        - using 'org.postgresql.Driver' as driver

        Args:
            table (str): table name
            storage_props (PostgreSqlDataProperties): PostgreSQL storage properties
            schema (StructType, optional): schema of data. Defaults to None.
            options (dict, optional): additional options for reading data. Defaults to None.

        Returns:
            DataFrame: data from PostgreSQL

        Notes:
            - schema is required with entire table column names and types, otherwise, it will be inferred from the data
        """

        if options is None:
            options = {}

        spark_options = {
            "driver": "org.postgresql.Driver",
        }

        options.update(spark_options)

        return self.read_from_sql(
            schema=schema,
            table=table,
            storage_props=storage_props,
            options=options,
        )

    def read_from_sql(
        self,
        table: str,
        storage_props: SqlDataProperties,
        schema: StructType = None,
        format: str = "jdbc",
        options: dict = None,
    ) -> DataFrame:
        """
        Read data from SQL storage (PostgreSQL, MySQL, MSSQL, etc.)

        Args:
            table (str): table name
            storage_props (SqlDataProperties): SQL storage properties
            schema (StructType, optional): schema of data. Defaults to None.
            format (str, optional): format to read data. Defaults to "jdbc".
            options (dict, optional): additional options for reading data. Defaults to None.

        Returns:
            DataFrame: data from SQL storage
        """

        if options is None:
            options = {}

        spark_options = {
            "url": storage_props.url,
            "dbtable": table,
        }

        options.update(spark_options)

        return self.read_from(schema=schema, format=format, options=options, path=table)

    def read_from_cassandra(
        self,
        table: str,
        storage_props: CassandraDataProperties,
        options: dict = None,
    ) -> DataFrame:
        """
        Read data from Cassandra storage

        - using 'org.apache.spark.sql.cassandra' as format
        - cassandra not allow schema, so it will be inferred from the data

        Args:
            table (str): table name
            storage_props (CassandraDataProperties): Cassandra storage properties
            options (dict, optional): additional options for reading data. Defaults to None.

        Returns:
            DataFrame: data from Cassandra
        """

        if options is None:
            options = {}

        spark_options = {
            "keyspace": storage_props.keyspace,
            "table": table,
        }

        options.update(spark_options)

        return self.read_from(
            schema=None,
            format="org.apache.spark.sql.cassandra",
            options=options,
            path=table,
        )

    def read_from_api(
        self,
        data_props: ApiDataModuleProperties,
        storage_props: ApiDataProperties,
        schema: StructType = None,
        success_handler: Callable[..., Any] = None,
        error_handler: Callable[..., Any] = None,
    ) -> DataFrame:
        """
        Read data from API

        TODO: need to rework this to support multiple return type (DataFrame, None). Temporary disable due to python 3.9 not supported Type union.

        Args:
            data_props (ApiDataModuleProperties): API module properties
            storage_props (ApiDataProperties):  API storage properties
            schema (StructType, optional): schema of data. Defaults to None.
            success_handler (Callable[..., Any], optional): success handler. Defaults to None.
            error_handler (Callable[..., Any], optional): error handler. Defaults to None.

        Returns:
            DataFrame: if success (status code 200), data will be returned as DataFrame, otherwise None
        """

        response = self.__request_api(
            self.__build_request_api_options(
                data_props=data_props, storage_props=storage_props
            )
        )
        if response.status_code == 200:
            datas = (
                response.json()
                if success_handler is None
                else success_handler(response.json())
            )

            return create_dataframe(
                spark=self.__spark_session, schema=schema, datas=datas
            )
        else:
            if error_handler:
                error_handler(response.json())

    def read_from(
        self,
        format: str,
        schema: StructType = None,
        path: str = None,
        options: dict = {},
    ) -> DataFrame:
        """
        Read data from storage

        ** use with caution, this method is for custom/override logic to read data **

        Args:
            format (str): format to read data
            schema (StructType, optional): schema of data. Defaults to None.
            path (str, optional): path to read data. Defaults to None.
            options (dict, optional): additional options for reading data. Defaults to {}.

        Returns:
            DataFrame: data from storage
        """

        if options is None:
            options = {}

        self.__logger.debug(f"reading data from type: {format}, table/path: {path}")

        reader = self.__spark_session.read.options(**options)

        if schema is not None:
            reader.schema(schema)

        if format == "csv":
            return reader.csv(path=path)
        elif format == "delta":
            return reader.format(format).load(path=path)
        else:
            return reader.format(format).load()

    def __build_request_api_options(
        self, data_props: ApiDataModuleProperties, storage_props: ApiDataProperties
    ) -> dict:
        options = {}
        headers = storage_props.headers
        method = str.lower(data_props.method)

        options["url"] = urljoin(
            storage_props.endpoint, storage_props.path + "/" + data_props.path
        )
        options["method"] = method
        options["parameters"] = data_props.parameters

        if not method:
            method = "get"

        if method == "post":
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"

            options["body"] = data_props.body

        options["headers"] = headers

        return options

    def __request_api(self, options: dict):
        url = options["url"]
        headers = options["headers"]
        method = options["method"]
        parameters = options["parameters"]

        if not method:
            method = "get"

        if method == "get":
            return requests.get(url, headers=headers, params=parameters)
        elif method == "post":
            body = options["body"]

            return requests.post(url, headers=headers, params=parameters, json=body)
