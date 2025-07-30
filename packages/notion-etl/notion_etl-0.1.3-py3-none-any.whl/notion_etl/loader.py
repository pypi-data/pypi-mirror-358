import os
from typing import Optional

from notion_client import Client

from notion_etl.database import NotionDataset
from notion_etl.page import NotionPageContents


class NotionDataLoader:
    def __init__(self, notion_token: Optional[str] = None):
        """
        Initialize the NotionDataClient class.

        :param notion_token: The Notion API token.
            If not provided, the token will be read from the environment variable NOTION_TOKEN.
        """
        self.client = Client(auth=notion_token or os.getenv("NOTION_TOKEN"))

    def get_database(self, database_id: str) -> NotionDataset:
        """
        Get a Notion database by its ID.

        :param database_id: The ID of the database to get.
        :param as_df: Whether to return the database as a DataFrame (Polars) or not.
        :param clean: Whether to return the DataFrame with clean data or not when as_df is True.
        """
        response = self.client.databases.query(database_id=database_id)
        results = response["results"]
        while response["next_cursor"]:
            response = self.client.databases.query(
                database_id=database_id, start_cursor=response["next_cursor"]
            )
            results.extend(response["results"])
        return NotionDataset(results)

    def get_page_contents(
        self,
        page_id: str,
    ) -> NotionPageContents:
        """
        Get the content of a Notion page by its ID.
        :param page_id: The ID of the page to get.
        :return: The content of the page as a dictionary.
        """
        response = self.client.blocks.children.list(block_id=page_id)
        results = response["results"]
        while response["next_cursor"]:
            response = self.client.blocks.children.list(
                block_id=page_id, start_cursor=response["next_cursor"]
            )
            results.extend(response["results"])
        return NotionPageContents(results)
