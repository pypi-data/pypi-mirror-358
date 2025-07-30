# pqcat
pqcat is a fast command-line tool for inspecting Parquet files.

## Installation

```bash
pip install pqcat
```


## Usage

```bash
$ pqcat head examples/retail.parquet -n 5
shape: (5, 8)
┌─────────┬────────────┬────────────┬───────────┬──────────┬──────────┬────────┬─────────────┐
│ OrderID ┆ CustomerID ┆ OrderDate  ┆ ProductID ┆ Category ┆ Quantity ┆ Price  ┆ TotalAmount │
│ ---     ┆ ---        ┆ ---        ┆ ---       ┆ ---      ┆ ---      ┆ ---    ┆ ---         │
│ str     ┆ str        ┆ str        ┆ str       ┆ str      ┆ i64      ┆ f64    ┆ f64         │
╞═════════╪════════════╪════════════╪═══════════╪══════════╪══════════╪════════╪═════════════╡
│ O0001   ┆ C1007      ┆ 2024-01-27 ┆ P016      ┆ Clothing ┆ 1        ┆ 159.57 ┆ 159.57      │
│ O0002   ┆ C1001      ┆ 2024-01-01 ┆ P011      ┆ Toys     ┆ 3        ┆ 10.54  ┆ 31.62       │
│ O0003   ┆ C1011      ┆ 2024-01-23 ┆ P011      ┆ Clothing ┆ 1        ┆ 82.04  ┆ 82.04       │
│ O0004   ┆ C1020      ┆ 2024-01-18 ┆ P006      ┆ Toys     ┆ 5        ┆ 174.84 ┆ 874.2       │
│ O0005   ┆ C1017      ┆ 2024-01-26 ┆ P001      ┆ Clothing ┆ 1        ┆ 16.62  ┆ 16.62       │
└─────────┴────────────┴────────────┴───────────┴──────────┴──────────┴────────┴─────────────┘
```

