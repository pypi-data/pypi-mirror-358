import typer
import polars as pl
from typing import Optional, List
import os

app = typer.Typer(
    help="Fast command-line tool for inspecting Parquet files", no_args_is_help=True
)

# === Constants ===
OUTPUT_FORMATS = {"table", "csv", "json", "jsonl", "markdown"}


# === Utility Functions ===
def parse_columns(columns: Optional[str]) -> Optional[list[str]]:
    return [c.strip() for c in columns.split(",")] if columns else None


def convert_value(val: str) -> object:
    val = val.strip("\"'")
    if val.lower() in ["true", "false"]:
        return val.lower() == "true"
    try:
        return int(val) if "." not in val else float(val)
    except ValueError:
        return val


def parse_filter_condition(condition: str) -> tuple[str, str, str]:
    operators = ["==", "!=", ">=", "<=", ">", "<", "contains", "startswith", "endswith"]
    for op in operators:
        if op in condition:
            parts = condition.split(op, 1)
            return parts[0].strip(), op, parts[1].strip()
    raise typer.BadParameter(f"Invalid filter condition: {condition}")


def build_filter(df: pl.DataFrame, filters: List[str]) -> Optional[pl.Expr]:
    exprs = []
    for cond in filters:
        col, op, val = parse_filter_condition(cond)
        if col not in df.columns:
            raise typer.BadParameter(f"Column '{col}' not found.")
        val = convert_value(val)
        col_expr = pl.col(col)
        match op:
            case "==":
                expr = col_expr == val
            case "!=":
                expr = col_expr != val
            case ">":
                expr = col_expr > val
            case "<":
                expr = col_expr < val
            case ">=":
                expr = col_expr >= val
            case "<=":
                expr = col_expr <= val
            case "contains":
                expr = col_expr.str.contains(str(val))
            case "startswith":
                expr = col_expr.str.starts_with(str(val))
            case "endswith":
                expr = col_expr.str.ends_with(str(val))
        exprs.append(expr)
    return exprs[0] if len(exprs) == 1 else pl.all(exprs)


def output(df: pl.DataFrame, format: str):
    match format:
        case "table":
            print(df)
        case "csv":
            print(df.write_csv())
        case "json":
            print(df.write_json())
        case "jsonl":
            for row in df.iter_rows(named=True):
                print(row)
        case "markdown":
            print(df.to_pandas().to_markdown(index=False))
        case _:
            raise typer.BadParameter(f"Unsupported format: {format}")


def validate_file_exists(file: str) -> None:
    if not os.path.isfile(file):
        raise typer.BadParameter(f"No such file: {file}")


def validate_num(num: int) -> None:
    if num < 1:
        raise typer.BadParameter("Number of rows must be at least 1.")


def read_filtered_df(
    file: str, columns: Optional[str], filters: Optional[List[str]]
) -> pl.DataFrame:
    validate_file_exists(file)
    cols = parse_columns(columns)
    df = pl.read_parquet(file, columns=cols)
    if filters:
        expr = build_filter(df, filters)
        df = df.filter(expr)
    return df


def common_options(
    num: Optional[int] = None,
    columns: Optional[str] = typer.Option(
        None, "--columns", "-c", help="Columns to display."
    ),
    filter: List[str] = typer.Option(None, "--filter", help="Filter conditions."),
    format: str = typer.Option("table", "--format", help="Output format."),
):
    if format not in OUTPUT_FORMATS:
        raise typer.BadParameter(f"Format must be one of {', '.join(OUTPUT_FORMATS)}")
    return num, columns, filter, format


# === CLI Commands ===
@app.command(help="Show first N rows")
def head(
    file: str,
    num: int = typer.Option(10, "--num", "-n", help="Number of rows to show"),
    columns: Optional[str] = typer.Option(
        None, "--columns", "-c", help="Columns to display. Example: 'column1,column2'"
    ),
    filter: List[str] = typer.Option(
        None, "--filter", help="Filter conditions. Example: 'column1>10'"
    ),
    format: str = typer.Option(
        "table", "--format", help="Output format: table, csv, json, jsonl, markdown"
    ),
):
    validate_num(num)
    df = read_filtered_df(file, columns, filter).head(num)
    output(df, format)


@app.command(help="Show last N rows")
def tail(
    file: str,
    num: int = typer.Option(10, "--num", "-n", help="Number of rows to show"),
    columns: Optional[str] = typer.Option(
        None, "--columns", "-c", help="Columns to display. Example: 'column1,column2'"
    ),
    filter: List[str] = typer.Option(
        None, "--filter", help="Filter conditions. Example: 'column1>10'"
    ),
    format: str = typer.Option(
        "table", "--format", help="Output format: table, csv, json, jsonl, markdown"
    ),
):
    validate_num(num)
    df = read_filtered_df(file, columns, filter).tail(num)
    output(df, format)


@app.command(name="cat", help="Show all rows")
def cat(
    file: str,
    columns: Optional[str] = typer.Option(
        None, "--columns", "-c", help="Columns to display. Example: 'column1,column2'"
    ),
    filter: List[str] = typer.Option(
        None, "--filter", help="Filter conditions. Example: 'column1>10'"
    ),
    format: str = typer.Option(
        "table", "--format", help="Output format: table, csv, json, jsonl, markdown"
    ),
):
    df = read_filtered_df(file, columns, filter)
    output(df, format)


@app.command(help="Show schema of Parquet file")
def schema(file: str):
    validate_file_exists(file)
    df = pl.read_parquet(file, n_rows=1)
    for name, dtype in zip(df.columns, df.dtypes):
        print(f"{name}: {dtype}")


@app.command(help="Show number of rows")
def row_count(file: str):
    validate_file_exists(file)
    df = pl.read_parquet(file)
    print(len(df))


@app.command(help="Show Parquet stats")
def stats(file: str):
    validate_file_exists(file)
    df = pl.read_parquet(file)
    print(df.describe())


if __name__ == "__main__":
    app()
