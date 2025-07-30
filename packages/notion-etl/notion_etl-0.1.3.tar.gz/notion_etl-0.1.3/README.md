# Notion ETL

<div align="center">
  <p>
    <a href="https://pypi.org/project/notion-etl"><img src="https://img.shields.io/pypi/v/notion-etl.svg" alt="PyPI"></a>
    <a href="LICENSE"><img src="https://img.shields.io/github/license/josersanvil/notion-etl" alt="License"></a>
    <a href="https://github.com/Josersanvil/notion-etl/actions/workflows/ci-lint-tests.yaml"><img src="https://github.com/Josersanvil/notion-etl/actions/workflows/ci-lint-tests.yaml/badge.svg" alt="Code Quality check"></a>
  </p>
</div>

A Python package for extracting, transforming, and loading data from Notion using Polars DataFrames and the Notion API Client.

The package provides a simple API for loading raw and clean data from Notion databases into Polars DataFrames, allowing for efficient data manipulation and analysis.

- [Notion ETL](#notion-etl)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Authentication](#authentication)
    - [Loading Data from a Notion Database](#loading-data-from-a-notion-database)
    - [Loading Data from a Notion Page](#loading-data-from-a-notion-page)
  - [Contributing](#contributing)

## Installation

The package is [available on PyPI](https://pypi.org/project/notion-etl/) and can be installed using pip:

```bash
pip install notion-etl
```

## Usage

### Authentication

Create a Notion integration and get your Notion API key. You can find instructions on how to do this in the [Notion API documentation](https://developers.notion.com/docs/getting-started).
Remember to share the pages and databases you want to access with your integration.

To authenticate, set your Notion API key as an environment variable:

```bash
export NOTION_TOKEN=secret_...
```

You can also set the token in your code:

```python
import os
from notion_etl.loader import NotionDataLoader

loader = NotionDataLoader(os.environ["NOTION_TOKEN"])
```

### Loading Data from a Notion Database

Use the `NotionDataLoader` class to load data from a Notion database. The `get_database` method retrieves the database and its records.

The database id can be found in the URL of the database page. For example, in the URL `https://www.notion.so/your_workspace/Database-Name-1234567890abcdef1234567890abcdef`, the database id is `1234567890abcdef1234567890abcdef`.

```python
from notion_etl.loader import NotionDataLoader

loader = NotionDataLoader()
database = loader.get_database("database_id")
database.records # List of records in the database
database.to_dataframe() # Convert to clean Polars DataFrame
database.to_dataframe(clean=False) # Convert to raw Polars DataFrame
```

### Loading Data from a Notion Page

For loading data from a Notion page, use the `get_page_contents` method. The results of a page can be converted to a Polars DataFrame, plain text, or markdown.

Same as with the database, the page id can be found in the URL of the page. For example, in the URL `https://www.notion.so/your_workspace/Page-Name-1234567890abcdef1234567890abcdef`, the page id is `1234567890abcdef1234567890abcdef`.

```python
from notion_etl.loader import NotionDataLoader

loader = NotionDataLoader()
page = loader.get_page_contents("page_id")
print(page.as_plain_text()) # Print the page content as plain text
print(page.as_markdown()) # Print the page content as markdown
page.as_dataframe() # Convert to Polars DataFrame, every block in the page is a row in the DataFrame
```

## Contributing

You can install the package using [uv](https://docs.astral.sh/uv/)

First install `uv` with:

```bash
pip install uv
```

Then create the environment with:

```bash
uv sync
```

You can activate the virtual environment with `source venv/bin/activate` or you can run commands with `uv run`. For example:

```bash
uv run pytest tests
```
