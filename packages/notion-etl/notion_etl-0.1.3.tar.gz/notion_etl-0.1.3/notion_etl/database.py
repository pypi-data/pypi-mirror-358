import logging
from typing import Any, BinaryIO, Mapping, Optional, TextIO

import polars as pl

_pl_dtypes = {
    "number": pl.Float64(),
    "title": pl.Utf8(),
    "rich_text": pl.Utf8(),
    "select": pl.Utf8(),
    "date": pl.Date(),
    "relation": pl.Utf8(),
    "checkbox": pl.Boolean(),
    "files": pl.Utf8(),
    "multi_select": pl.List(pl.Utf8),
}


class NotionDataset:
    """
    Objects from this class represent the results of a Notion database
    that can be exported to a DataFrame or other formats.
    """

    properties_col = "properties"

    def __init__(self, results: list[dict[str, Any]]):
        """
        :param results: The results of the Notion API call to get the database.
        """
        self._records = results

    def __repr__(self) -> str:
        return f"<{self.__str__()}>"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(records={self.size})"

    @property
    def logger(self) -> logging.Logger:
        """
        Logger for the class.
        """
        return logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def size(self) -> int:
        """
        The number of records in the database.
        """
        return len(self.records)

    @property
    def records(self) -> list[dict[str, Any]]:
        """
        The raw data of the database as returned by the Notion API.
        """
        return self._records

    def to_csv(self, path: str | BinaryIO | TextIO, clean: bool = True) -> None:
        """
        Export the database to a CSV file.

        :param path: The path to save the CSV file.
        :param clean: Whether to clean the DataFrame or not.
            If set to False the DataFrame will contain all the
            columns as returned by the Notion API.
        """
        self.to_dataframe(clean=clean).write_csv(path)

    def to_dataframe(self, clean: bool = True) -> pl.DataFrame:
        """
        Convert the database to a Polars DataFrame.

        :param clean: Whether to clean the DataFrame or not.
            If set to False, the DataFrame will contain all the
            columns as returned by the Notion API.
        """
        df = pl.from_records(self.records)
        if clean:
            return self._clean_pl_df(df)
        return df

    def _get_normalised_name(self, col: str) -> str:
        """
        Normalize the column names to be used in the DataFrame.
        """
        return "_".join(col.strip().lower().split())

    def _rename_df_properties(
        self,
        df: pl.DataFrame,
        renames: Mapping[str, str],
    ) -> pl.DataFrame:
        """
        Rename all the fields in the properties column
        of type 'struct' of the DataFrame to the new names.
        """
        fieldnames = [field.name for field in df.schema[self.properties_col].fields]  # type: ignore
        renamed_ordered = {original: renames[original] for original in fieldnames}
        df = df.with_columns(
            [
                pl.col(self.properties_col)
                .struct.rename_fields(list(renamed_ordered.values()))
                .alias(self.properties_col)
            ]
        )
        return df

    def _clean_pl_df(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Clean the Polars DataFrame by renaming the columns
        and extracting the values from the properties column.
        """
        df_schema = dict(df.schema[self.properties_col])  # type: ignore
        normal_colnames = {
            col: self._get_normalised_name(col) for col in df_schema.keys()
        }
        df_cols_data = {
            normal_colnames[col]: {"value": list(val)[2][0], "colname": col}
            for col, val in df_schema.items()
        }
        cleaned_df = self._rename_df_properties(df, normal_colnames)
        return cleaned_df.select(
            *[
                self._pl_get_col_value(
                    col_name,
                    col_data["value"],
                    cleaned_df,
                    alias=col_data["colname"],
                )
                for col_name, col_data in df_cols_data.items()
            ],
            pl.col("id").alias("_page_id"),
            pl.col("url").alias("_page_url"),
            pl.col("public_url").alias("_page_public_url"),
            pl.col("created_time").alias("_created_at").cast(pl.Datetime),
            pl.col("last_edited_time").alias("_last_edited_at").cast(pl.Datetime),
        )

    def _get_properties_col_field(
        self, field_name: str, properties_col: pl.Series
    ) -> pl.Series:
        """
        Get the field object that is inside the properties column
        of type 'struct' of the DataFrame.
        """
        return properties_col.struct.field(field_name)

    def _pl_get_col_value(
        self,
        col_name: str,
        col_type: str,
        cleaned_df: pl.DataFrame,
        alias: Optional[str] = None,
    ) -> pl.Series | pl.Expr:
        """
        Get the Polars expression for a column value based on
        the column name and type as returned by the Notion API.
        """
        if not alias:
            alias = col_name
        col = (
            self._get_properties_col_field(col_name, cleaned_df[self.properties_col])
            if self.properties_col
            else cleaned_df[col_name]
        )
        col_schema = dict(col.struct.schema)
        col_struct = col.struct.field(col_type)
        col_schema_type = col_schema[col_type]
        col_value: pl.Expr | pl.Series = pl.lit(None)
        match col_type:
            case "rich_text" | "title":
                if col_schema_type.is_(pl.List(pl.Null)):
                    col_value = col_value.cast(_pl_dtypes[col_type])
                else:
                    col_value = col_struct.list.get(0, null_on_oob=True)
                    col_value = (
                        pl.when(col_value.is_null())
                        .then(pl.lit(None))
                        .otherwise(
                            (
                                col_value.struct.field("text")
                                .struct.field("content")
                                .cast(_pl_dtypes[col_type])
                            )
                        )
                    )
            case "number" | "checkbox":
                col_value = col_struct.cast(_pl_dtypes[col_type])
            case "select":
                col_value = col_struct.struct.field("name").cast(_pl_dtypes[col_type])
            case "date":
                col_value = col_struct.struct.field("start").cast(_pl_dtypes[col_type])
            case "relation":
                col_value = (
                    col_struct.list.get(0, null_on_oob=True)
                    .struct.field("id")
                    .cast(_pl_dtypes[col_type])
                )
            case "files":
                col_value = (
                    col_struct.list.get(0, null_on_oob=True)
                    # .struct.field("file")
                    # .struct.field("url")
                    # .cast(pl.Utf8)
                )
            case "rollup":
                return (
                    col_struct.struct.field("array")
                    .list.get(0, null_on_oob=True)
                    .alias(alias)
                )
            case "formula":
                col_value = col_struct
            case "url":
                col_value = col_struct
            case "multi_select":
                col_value = col_struct.list.eval(
                    pl.element().struct.field("name")
                ).cast(_pl_dtypes[col_type])
            case _:
                self.logger.debug(
                    f"Unknown column type '{col_type}' for column '{col_name}'. "
                    "Returning the original column."
                )
                col_value = col_struct
        return col_value.alias(alias)
