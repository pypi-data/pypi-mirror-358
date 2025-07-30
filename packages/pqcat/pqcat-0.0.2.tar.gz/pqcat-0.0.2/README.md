[![pypi](https://img.shields.io/pypi/v/pqcat.svg)](https://pypi.python.org/pypi/pqcat) [![Release Build](https://github.com/speed1313/pqcat/actions/workflows/publish.yml/badge.svg)](https://github.com/speed1313/pqcat/actions/workflows/publish.yml) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
# pqcat

Fast command-line tool for inspecting Parquet files.

## Installation

```bash
pip install pqcat
```


## Usage

```bash
$ pqcat
Usage: pqcat [OPTIONS] COMMAND [ARGS]...

 Fast CLI tool for Parquet using Polars


╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                │
│ --show-completion             Show completion for the current shell, to copy it or customize the       │
│                               installation.                                                            │
│ --help                        Show this message and exit.                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────╮
│ head        Show first N rows                                                                          │
│ tail        Show last N rows                                                                           │
│ cat         Show all rows (alias for show)                                                             │
│ schema      Show schema of Parquet file                                                                │
│ row-count   Show number of rows                                                                        │
│ stats       Show Parquet stats                                                                         │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Usage: pqcat [OPTIONS] COMMAND [ARGS]...
```


### cat command
```bash
$ pqcat cat examples/retail.parquet
shape: (50, 8)
┌─────────┬────────────┬────────────┬───────────┬───────────┬──────────┬────────┬─────────────┐
│ OrderID ┆ CustomerID ┆ OrderDate  ┆ ProductID ┆ Category  ┆ Quantity ┆ Price  ┆ TotalAmount │
│ ---     ┆ ---        ┆ ---        ┆ ---       ┆ ---       ┆ ---      ┆ ---    ┆ ---         │
│ str     ┆ str        ┆ str        ┆ str       ┆ str       ┆ i64      ┆ f64    ┆ f64         │
╞═════════╪════════════╪════════════╪═══════════╪═══════════╪══════════╪════════╪═════════════╡
│ O0001   ┆ C1007      ┆ 2024-01-27 ┆ P016      ┆ Clothing  ┆ 1        ┆ 159.57 ┆ 159.57      │
│ O0002   ┆ C1001      ┆ 2024-01-01 ┆ P011      ┆ Toys      ┆ 3        ┆ 10.54  ┆ 31.62       │
│ O0003   ┆ C1011      ┆ 2024-01-23 ┆ P011      ┆ Clothing  ┆ 1        ┆ 82.04  ┆ 82.04       │
│ O0004   ┆ C1020      ┆ 2024-01-18 ┆ P006      ┆ Toys      ┆ 5        ┆ 174.84 ┆ 874.2       │
│ O0005   ┆ C1017      ┆ 2024-01-26 ┆ P001      ┆ Clothing  ┆ 1        ┆ 16.62  ┆ 16.62       │
│ …       ┆ …          ┆ …          ┆ …         ┆ …         ┆ …        ┆ …      ┆ …           │
│ O0046   ┆ C1010      ┆ 2024-01-25 ┆ P007      ┆ Toys      ┆ 4        ┆ 93.06  ┆ 372.24      │
│ O0047   ┆ C1017      ┆ 2024-01-13 ┆ P009      ┆ Books     ┆ 5        ┆ 14.31  ┆ 71.55       │
│ O0048   ┆ C1013      ┆ 2024-01-28 ┆ P015      ┆ Books     ┆ 5        ┆ 106.63 ┆ 533.15      │
│ O0049   ┆ C1005      ┆ 2024-01-27 ┆ P011      ┆ Toys      ┆ 1        ┆ 105.6  ┆ 105.6       │
│ O0050   ┆ C1000      ┆ 2024-01-06 ┆ P019      ┆ Groceries ┆ 2        ┆ 47.31  ┆ 94.62       │
└─────────┴────────────┴────────────┴───────────┴───────────┴──────────┴────────┴─────────────┘
```

### head command
```bash
$ pqcat head examples/retail.parquet -n 5 --columns Category,Price
shape: (5, 2)
┌──────────┬────────┐
│ Category ┆ Price  │
│ ---      ┆ ---    │
│ str      ┆ f64    │
╞══════════╪════════╡
│ Clothing ┆ 159.57 │
│ Toys     ┆ 10.54  │
│ Clothing ┆ 82.04  │
│ Toys     ┆ 174.84 │
│ Clothing ┆ 16.62  │
└──────────┴────────┘
```

### schema command
```bash
$ pqcat schema examples/retail.parquet
OrderID: String
CustomerID: String
OrderDate: String
ProductID: String
Category: String
Quantity: Int64
Price: Float64
TotalAmount: Float64
```

### row-count command
```bash
$ pqcat row-count examples/retail.parquet
50
```

### stats command
```bash
$ pqcat stats examples/retail.parquet
┌────────────┬─────────┬────────────┬────────────┬───┬──────────┬──────────┬───────────┬─────────────┐
│ statistic  ┆ OrderID ┆ CustomerID ┆ OrderDate  ┆ … ┆ Category ┆ Quantity ┆ Price     ┆ TotalAmount │
│ ---        ┆ ---     ┆ ---        ┆ ---        ┆   ┆ ---      ┆ ---      ┆ ---       ┆ ---         │
│ str        ┆ str     ┆ str        ┆ str        ┆   ┆ str      ┆ f64      ┆ f64       ┆ f64         │
╞════════════╪═════════╪════════════╪════════════╪═══╪══════════╪══════════╪═══════════╪═════════════╡
│ count      ┆ 50      ┆ 50         ┆ 50         ┆ … ┆ 50       ┆ 50.0     ┆ 50.0      ┆ 50.0        │
│ null_count ┆ 0       ┆ 0          ┆ 0          ┆ … ┆ 0        ┆ 0.0      ┆ 0.0       ┆ 0.0         │
│ mean       ┆ null    ┆ null       ┆ null       ┆ … ┆ null     ┆ 2.74     ┆ 88.6722   ┆ 231.8516    │
│ std        ┆ null    ┆ null       ┆ null       ┆ … ┆ null     ┆ 1.454199 ┆ 59.740505 ┆ 201.475002  │
│ min        ┆ O0001   ┆ C1000      ┆ 2024-01-01 ┆ … ┆ Books    ┆ 1.0      ┆ 10.54     ┆ 11.73       │
│ 25%        ┆ null    ┆ null       ┆ null       ┆ … ┆ null     ┆ 1.0      ┆ 24.91     ┆ 76.8        │
│ 50%        ┆ null    ┆ null       ┆ null       ┆ … ┆ null     ┆ 3.0      ┆ 93.06     ┆ 159.57      │
│ 75%        ┆ null    ┆ null       ┆ null       ┆ … ┆ null     ┆ 4.0      ┆ 147.87    ┆ 372.24      │
│ max        ┆ O0050   ┆ C1020      ┆ 2024-01-30 ┆ … ┆ Toys     ┆ 5.0      ┆ 197.7     ┆ 874.2       │
└────────────┴─────────┴────────────┴────────────┴───┴──────────┴──────────┴───────────┴─────────────┘
```


## References
This project is inspired by https://github.com/hangxie/parquet-tools.