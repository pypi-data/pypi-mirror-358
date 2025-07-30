import re
import uuid

from cloe_logging import LoggerFactory
from cloe_metadata import base
from cloe_metadata.base.repository.database.column import Column
from cloe_metadata.base.repository.database.database import Database, Databases
from cloe_metadata.base.repository.database.schema import Schema
from cloe_metadata.base.repository.database.table import Table
from pydantic import BaseModel

logger = LoggerFactory.get_logger(handler_types=["console", "file"], filename="databricks_crawler.log")


class DatabricksCrawler(BaseModel):
    """
    DatabricksCrawler extracts metadata from Databricks workspaces. It collects catalogs, schemas,
    optionally tables, and column information.
    """

    ignore_tables: bool = False
    ignore_columns: bool = False
    catalog_filter: str | None = None  # User-provided pattern
    catalog_regex: re.Pattern | None = None  # Compiled regex
    databases: base.Databases = base.Databases(databases=[])

    def __init__(self, **data):
        """
        Initialization and compilation of the regex pattern from catalog_filter if one if provided.
        """
        super().__init__(**data)

        # Compile regex if a catalog pattern is provided
        if self.catalog_filter:
            try:
                self.catalog_regex = re.compile(self.catalog_filter, re.IGNORECASE)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern provided: {self.catalog_filter} - {e}") from e

    def crawl(self, client):
        """
        Initiates the crawling process by collecting catalogs from the Databricks workspace.
        """
        self.databases = Databases(databases=self._process_catalogs(client))

    def _process_catalogs(self, client):
        """
        Fetches all catalogs from the Databricks workspace and processes them.
        """
        logger.info("Start crawling...")

        catalogs = []
        for catalog in client.catalogs.list():
            if catalog.name == "sytem" or (self.catalog_regex and not self.catalog_regex.match(catalog.name)):
                # Regex filtering, skip catalogs that do not match the provided filter pattern
                continue
            catalogs.append(
                Database(
                    id=uuid.uuid4(),
                    display_name=None,
                    name=catalog.name,
                    schemas=self._process_schemas(client, catalog),
                )
            )
        return catalogs

    def _process_schemas(self, client, catalog):
        """
        Fetches all schemas within a catalog and processes them.
        """
        schemas = []
        for schema in client.schemas.list(catalog.name):
            tables = []
            if not self.ignore_tables:
                tables = self._process_tables(client, catalog, schema)
            schemas.append(Schema(id=uuid.uuid4(), name=schema.name, tables=tables))
        return schemas

    def _process_tables(self, client, catalog, schema):
        """
        Fetches all tables within a schema and processes them.
        """
        tables = []
        for table in client.tables.list(catalog.name, schema.name):
            columns = []
            if not self.ignore_columns:
                columns = self._process_columns(table)
            tables.append(Table(id=uuid.uuid4(), level=None, name=table.name, columns=columns))
        return tables

    def _process_columns(self, table):
        """
        Fetches all columns within a table and processes them.
        """
        columns = []
        for column in table.columns:
            columns.append(
                Column(
                    comment=column.comment,
                    constraints=None,
                    data_type=column.type_text,
                    data_type_length=None,
                    data_type_numeric_scale=column.type_scale,
                    data_type_precision=column.type_precision,
                    is_key=None,
                    is_nullable=column.nullable,
                    labels=None,
                    name=column.name,
                    ordinal_position=None,
                )
            )
        return columns

    def list_catalogs(self):
        """
        Retrieves all catalogs discovered during crawling.
        """
        return [catalog.name for catalog in self.databases.databases]

    def list_schemas(self):
        """
        Retrieves all schemas per catalog discovered during crawling.
        """
        schemas = {}
        for catalog in self.databases.databases:
            schemas[catalog.name] = [schema.name for schema in catalog.schemas]
        return schemas
