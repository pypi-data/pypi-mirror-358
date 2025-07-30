import re

import pytest

from cloe_dbx_crawler.databricks_crawler import DatabricksCrawler


def test_list_catalogs_simple():
    crawler = DatabricksCrawler()

    # Inject mock data directly
    crawler.databases.databases = [
        type("MockCatalog", (), {"name": "catalog_one"})(),
        type("MockCatalog", (), {"name": "catalog_two"})(),
    ]

    assert crawler.list_catalogs() == ["catalog_one", "catalog_two"]


def test_list_schemas_simple():
    crawler = DatabricksCrawler()
    crawler.databases.databases = [
        type(
            "MockCatalog",
            (),
            {
                "name": "catalog1",
                "schemas": [
                    type("MockSchema", (), {"name": "schema1"})(),
                    type("MockSchema", (), {"name": "schema2"})(),
                ],
            },
        )(),
        type("MockCatalog", (), {"name": "catalog2", "schemas": [type("MockSchema", (), {"name": "schema3"})()]})(),
    ]
    result = crawler.list_schemas()
    expected = {"catalog1": ["schema1", "schema2"], "catalog2": ["schema3"]}
    assert result == expected


def test_regex_compilation_valid():
    crawler = DatabricksCrawler(catalog_filter="^test.*$")
    assert isinstance(crawler.catalog_regex, re.Pattern)


def test_regex_compilation_invalid():
    with pytest.raises(ValueError):
        DatabricksCrawler(catalog_filter="(unclosed")


def test_empty_catalogs_list():
    crawler = DatabricksCrawler()
    crawler.databases.databases = []
    assert crawler.list_catalogs() == []


def test_empty_schemas_list():
    crawler = DatabricksCrawler()
    crawler.databases.databases = [type("MockCatalog", (), {"name": "empty_catalog", "schemas": []})()]
    assert crawler.list_schemas() == {"empty_catalog": []}


def test_crawler_with_no_filter():
    crawler = DatabricksCrawler()
    assert crawler.catalog_filter is None
    assert crawler.catalog_regex is None


def test_init_with_valid_regex_sets_filter_and_regex():
    crawler = DatabricksCrawler(catalog_filter="^data_.*$")
    assert crawler.catalog_filter == "^data_.*$"
    assert crawler.catalog_regex.match("data_lake")


def test_catalog_regex_does_not_match():
    crawler = DatabricksCrawler(catalog_filter="^abc$")
    assert crawler.catalog_regex.match("xyz") is None


def test_list_catalogs_single_entry():
    crawler = DatabricksCrawler()
    crawler.databases.databases = [type("MockCatalog", (), {"name": "only_catalog"})()]
    assert crawler.list_catalogs() == ["only_catalog"]


def test_list_schemas_multiple_empty():
    crawler = DatabricksCrawler()
    crawler.databases.databases = [
        type("MockCatalog", (), {"name": "cat1", "schemas": []})(),
        type("MockCatalog", (), {"name": "cat2", "schemas": []})(),
    ]
    result = crawler.list_schemas()
    assert result == {"cat1": [], "cat2": []}


def test_list_schemas_mixed():
    crawler = DatabricksCrawler()
    crawler.databases.databases = [
        type("MockCatalog", (), {"name": "cat1", "schemas": [type("MockSchema", (), {"name": "s1"})()]})(),
        type("MockCatalog", (), {"name": "cat2", "schemas": []})(),
    ]
    result = crawler.list_schemas()
    assert result == {"cat1": ["s1"], "cat2": []}


def test_init_with_empty_data():
    crawler = DatabricksCrawler()
    assert isinstance(crawler, DatabricksCrawler)
    assert crawler.ignore_tables is False
    assert crawler.ignore_columns is False
    assert crawler.catalog_filter is None
    assert crawler.catalog_regex is None
    assert crawler.databases.databases == []


def test_regex_match_exact():
    crawler = DatabricksCrawler(catalog_filter="^abc$")
    assert crawler.catalog_regex.match("abc")
    assert not crawler.catalog_regex.match("abcd")


def test_process_catalogs_with_valid_catalogs():
    crawler = DatabricksCrawler()

    class Catalog:
        def __init__(self, name):
            self.name = name

    class Client:
        class catalogs:
            @staticmethod
            def list():
                return [
                    Catalog("catalog1"),
                    Catalog("sytem"),  # should be skipped
                    Catalog("catalog2"),
                ]

        class schemas:
            @staticmethod
            def list(name):
                return []

    result = crawler._process_catalogs(Client())
    names = [catalog.name for catalog in result]
    assert names == ["catalog1", "catalog2"]


def test_process_schemas_with_and_without_tables():
    crawler = DatabricksCrawler(ignore_tables=True)

    class Schema:
        def __init__(self, name):
            self.name = name

    class Catalog:
        name = "catalog1"

    class Client:
        class schemas:
            @staticmethod
            def list(name):
                return [Schema("schema1"), Schema("schema2")]

    schemas = crawler._process_schemas(Client(), Catalog())
    names = [schema.name for schema in schemas]
    assert names == ["schema1", "schema2"]
    assert all(schema.tables == [] for schema in schemas)


def test_process_columns_extracts_data():
    crawler = DatabricksCrawler()

    class ColumnObj:
        def __init__(self):
            self.comment = "comment"
            self.type_text = "STRING"
            self.type_scale = None
            self.type_precision = None
            self.nullable = True
            self.name = "col1"

    class Table:
        columns = [ColumnObj()]

    result = crawler._process_columns(Table())
    assert len(result) == 1
    assert result[0].name == "col1"
    assert result[0].data_type == "STRING"
