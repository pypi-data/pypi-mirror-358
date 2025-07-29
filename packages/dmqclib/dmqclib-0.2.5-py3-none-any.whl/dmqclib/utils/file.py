import os
from typing import Dict

import polars as pl


def read_input_file(
    input_file: str, file_type: str = None, options: Dict = None
) -> pl.DataFrame:
    """
    Reads an input file into a Polars DataFrame. Supports parquet, tsv(.gz), and csv(.gz).

    Parameters:
    -----------
    input_file : str
        The path to the file to be read.
    file_type : str, optional
        The file type: one of 'parquet', 'tsv', 'tsv.gz', 'csv', or 'csv.gz'.
        If empty or None, it will be inferred from the file name.
    options : Dict, optional
        A dictionary of additional reading options to pass to the Polars function.

    Returns:
    --------
    pl.DataFrame
        The Polars DataFrame loaded with the file contents.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"The file '{input_file}' does not exist.")

    if options is None:
        options = {}

    # If file_type is not provided, infer it from file extension.
    if not file_type:
        filename = os.path.basename(input_file).lower()
        if filename.endswith(".parquet"):
            file_type = "parquet"
        elif filename.endswith(".tsv.gz"):
            file_type = "tsv.gz"
        elif filename.endswith(".tsv"):
            file_type = "tsv"
        elif filename.endswith(".csv.gz"):
            file_type = "csv.gz"
        elif filename.endswith(".csv"):
            file_type = "csv"
        else:
            raise ValueError(
                "Could not infer file type automatically. Please specify 'file_type' explicitly."
            )

    if file_type == "parquet":
        df = pl.read_parquet(input_file, **options)

    elif file_type in ("tsv", "tsv.gz"):
        # Polars can handle gzip automatically, so we only need to set the separator.
        df = pl.read_csv(input_file, separator="\t", **options)

    elif file_type in ("csv", "csv.gz"):
        # Similarly, Polars handles gzip automatically for CSV.
        df = pl.read_csv(input_file, **options)

    else:
        raise ValueError(
            f"Unsupported file_type '{file_type}'. Must be one of: "
            "'parquet', 'tsv', 'tsv.gz', 'csv', 'csv.gz'."
        )

    return df
