import argparse
import polars as pl
import sys
from typing import List, Tuple, Optional


def parse_columns(columns):
    return [c.strip() for c in columns.split(",")] if columns else None


def parse_filter_condition(condition: str) -> Tuple[str, str, str]:
    """
    Parse a single filter condition like 'col1>5' or 'col2==value'
    Returns (column, operator, value)
    """
    # Support operators: ==, !=, >=, <=, >, <, contains, startswith, endswith
    operators = [">=", "<=", "==", "!=", ">", "<", "contains", "startswith", "endswith"]

    for op in operators:
        if op in condition:
            parts = condition.split(op, 1)
            if len(parts) == 2:
                col = parts[0].strip()
                val = parts[1].strip()
                return col, op, val

    raise ValueError(f"Invalid filter condition: {condition}")


def convert_value(value: str, column_type):
    """Convert string value to appropriate type based on column"""
    value = value.strip("'\"")  # Remove quotes if present

    if value.lower() in ["true", "false"]:
        return value.lower() == "true"

    try:
        if "." in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        return value  # Keep as string


def build_polars_filter(df: pl.DataFrame, filter_conditions: List[str]) -> pl.Expr:
    """
    Build Polars filter expression from list of conditions
    """
    if not filter_conditions:
        return None

    filters = []

    for condition in filter_conditions:
        col_name, operator, value = parse_filter_condition(condition)

        if col_name not in df.columns:
            raise ValueError(f"Column '{col_name}' not found in dataframe")

        # Get column reference
        col = pl.col(col_name)

        # Convert value to appropriate type
        converted_value = convert_value(value, df[col_name].dtype)

        # Build filter expression
        if operator == "==":
            filter_expr = col == converted_value
        elif operator == "!=":
            filter_expr = col != converted_value
        elif operator == ">":
            filter_expr = col > converted_value
        elif operator == "<":
            filter_expr = col < converted_value
        elif operator == ">=":
            filter_expr = col >= converted_value
        elif operator == "<=":
            filter_expr = col <= converted_value
        elif operator == "contains":
            filter_expr = col.str.contains(str(converted_value))
        elif operator == "startswith":
            filter_expr = col.str.starts_with(str(converted_value))
        elif operator == "endswith":
            filter_expr = col.str.ends_with(str(converted_value))
        else:
            raise ValueError(f"Unsupported operator: {operator}")

        filters.append(filter_expr)

    # Combine all filters with AND
    combined_filter = filters[0]
    for f in filters[1:]:
        combined_filter = combined_filter & f

    return combined_filter


def apply_filter(df: pl.DataFrame, filter_args: Optional[List[str]]) -> pl.DataFrame:
    """Apply filters to dataframe"""
    if not filter_args:
        return df

    try:
        filter_expr = build_polars_filter(df, filter_args)
        if filter_expr is not None:
            df = df.filter(filter_expr)
    except Exception as e:
        print(f"Invalid filter: {e}", file=sys.stderr)
        sys.exit(1)

    return df


def output(df, fmt):
    if fmt == "table":
        print(df)
    elif fmt == "csv":
        print(df.write_csv())
    elif fmt == "json":
        print(df.write_json(row_oriented=True))
    else:
        print(f"Unsupported format: {fmt}", file=sys.stderr)
        sys.exit(1)


def read_head(args):
    df = pl.read_parquet(
        args.file, columns=parse_columns(args.columns), n_rows=args.num
    )
    df = apply_filter(df, args.filter)
    output(df, args.format)


def read_tail(args):
    df = pl.read_parquet(args.file, columns=parse_columns(args.columns))
    df = apply_filter(df, args.filter)
    df = df.tail(args.num)
    output(df, args.format)


def read_all(args):
    df = pl.read_parquet(args.file, columns=parse_columns(args.columns))
    df = apply_filter(df, args.filter)
    output(df, args.format)


def main():
    parser = argparse.ArgumentParser(
        prog="pqcat", description="Fast CLI tool for Parquet using Polars"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_args(p):
        p.add_argument("file", type=str, help="Parquet file path")
        p.add_argument("-n", "--num", type=int, default=10, help="Number of rows")
        p.add_argument("--columns", type=str, help="Comma-separated list of columns")
        p.add_argument(
            "--format",
            choices=["table", "csv", "json"],
            default="table",
            help="Output format",
        )
        p.add_argument(
            "--filter",
            "-f",
            action="append",
            help="Filter condition (e.g., 'age>25', 'name==John'). Can be used multiple times for AND conditions.",
        )

    head_parser = subparsers.add_parser("head", help="Show first N rows")
    add_common_args(head_parser)
    head_parser.set_defaults(func=read_head)

    tail_parser = subparsers.add_parser("tail", help="Show last N rows")
    add_common_args(tail_parser)
    tail_parser.set_defaults(func=read_tail)

    # Show all rows (cat/show command)
    show_parser = subparsers.add_parser("show", help="Show all rows")
    show_parser.add_argument("file", type=str, help="Parquet file path")
    show_parser.add_argument(
        "--columns", type=str, help="Comma-separated list of columns"
    )
    show_parser.add_argument(
        "--format",
        choices=["table", "csv", "json"],
        default="table",
        help="Output format",
    )
    show_parser.add_argument(
        "--filter",
        "-f",
        action="append",
        help="Filter condition (e.g., 'age>25', 'name==John'). Can be used multiple times for AND conditions.",
    )
    show_parser.set_defaults(func=read_all)

    # Add cat as alias for show
    cat_parser = subparsers.add_parser("cat", help="Show all rows (alias for show)")
    cat_parser.add_argument("file", type=str, help="Parquet file path")
    cat_parser.add_argument(
        "--columns", type=str, help="Comma-separated list of columns"
    )
    cat_parser.add_argument(
        "--format",
        choices=["table", "csv", "json"],
        default="table",
        help="Output format",
    )
    cat_parser.add_argument(
        "--filter",
        "-f",
        action="append",
        help="Filter condition (e.g., 'age>25', 'name==John'). Can be used multiple times for AND conditions.",
    )
    cat_parser.set_defaults(func=read_all)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
