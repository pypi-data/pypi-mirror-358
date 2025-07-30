import typer
import polars as pl
from typing import Optional, List

app = typer.Typer(help="Fast CLI tool for Parquet using Polars", no_args_is_help=True)


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
        col_expr = pl.col(col)
        val = convert_value(val)
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
    return exprs[0] & exprs[1] if len(exprs) > 1 else exprs[0] if exprs else None


def output(df: pl.DataFrame, format: str):
    if format == "table":
        print(df)
    elif format == "csv":
        print(df.write_csv())
    elif format == "json":
        print(df.write_json())
    elif format == "markdown":
        pdf = df.to_pandas()
        print(pdf.to_markdown(index=False))
    else:
        raise typer.BadParameter(f"Unsupported format: {format}")


# === Core Commands ===
@app.command(help="Show first N rows")
def head(
    file: str,
    num: int = typer.Option(10, "--num", "-n", help="Number of rows to show"),
    columns: Optional[str] = None,
    filter: List[str] = typer.Option(None, "--filter", "-f"),
    format: str = "table",
):
    df = pl.read_parquet(file, columns=parse_columns(columns), n_rows=num * 5)
    if filter:
        df = df.filter(build_filter(df, filter))
    df = df.head(num)
    output(df, format)


@app.command(help="Show last N rows")
def tail(
    file: str,
    num: int = typer.Option(10, "--num", "-n", help="Number of rows to show"),
    columns: Optional[str] = None,
    filter: List[str] = typer.Option(None, "--filter", "-f"),
    format: str = "table",
):
    df = pl.read_parquet(file, columns=parse_columns(columns))
    if filter:
        df = df.filter(build_filter(df, filter))
    df = df.tail(num)
    output(df, format)


@app.command(name="cat", help="Show all rows (alias for show)")
def cat(
    file: str,
    columns: Optional[str] = None,
    filter: List[str] = typer.Option(None, "--filter", "-f"),
    format: str = "table",
):
    df = pl.read_parquet(file, columns=parse_columns(columns))
    if filter:
        df = df.filter(build_filter(df, filter))
    output(df, format)


@app.command(help="Show schema of Parquet file")
def schema(file: str):
    df = pl.read_parquet(file, n_rows=1)
    for name, dtype in zip(df.columns, df.dtypes):
        print(f"{name}: {dtype}")


@app.command(help="Show number of rows")
def row_count(file: str):
    df = pl.read_parquet(file)
    print(f"{len(df)}")


@app.command(help="Show Parquet stats")
def stats(file: str):
    df = pl.read_parquet(file)
    print(df.describe())


if __name__ == "__main__":
    app()
