import logging
import pathlib
from typing import Annotated, Optional

import typer
from cloe_dbx_connector import databricks_connection

from cloe_dbx_crawler.databricks_crawler import DatabricksCrawler

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def crawl(
    output_json_path: Annotated[
        pathlib.Path,
        typer.Argument(help="Path to save the crawled output to."),
    ],
    ignore_columns: Annotated[
        bool,
        typer.Option(
            help="Ignore columns of tables and just retrieve information about the table itself.",
        ),
    ] = False,
    ignore_tables: Annotated[
        bool,
        typer.Option(
            help="Ignore tables and just retrieve information about the higher level objects.",
        ),
    ] = False,
    catalog_filter: Annotated[
        Optional[str],  # noqa: UP007
        typer.Option(
            help="Filters catalogs based on defined filter. Is used as regex pattern. \
                If no filter defined, all catalogs (except the system catalog) are retrieved.",
        ),
    ] = None,
) -> None:
    """
    Crawls a databricks instance and writes the crawled
    metadata to JSON files stored in a specified folder.
    """
    connector = databricks_connection.DatabricksConnector.from_env()
    client = connector.get_workspace_client()

    crawler = DatabricksCrawler(
        ignore_tables=ignore_tables, ignore_columns=ignore_columns, catalog_filter=catalog_filter
    )
    crawler.crawl(client)
    databases = crawler.databases
    logger.info("Finished crawling, writing to disk...")
    databases.write_to_disk(output_path=output_json_path, delete_existing=True)
    logger.info(f"Crawler output is now stored at: {output_json_path}")
