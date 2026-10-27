# Inventory Stock Level Audit

A beginner-friendly data analytics project using **Python, Pandas, NumPy, Matplotlib, Streamlit, and MySQL**. It flags low stock, out-of-stock and overstock products, compares recorded stock with physical counts, estimates inventory value, and exports an audit report.

> The included CSV is synthetic demo data. Validate all thresholds and stock counts before using this for real inventory decisions.

## Features

- Interactive Streamlit dashboard with category, stock-status, and audit-result filters
- KPIs for product count, physical units, inventory value, low stock, out-of-stock, overstock, and discrepancies
- Stock variance and variance value calculations
- Suggested reorder quantity up to the maximum stock level
- Charts for stock status and category valuation
- Searchable audit table and CSV report download
- MySQL schema and example SQL queries
- Basic automated tests

## Project structure

```text
inventory-stock-level-audit/
├── app.py
├── requirements.txt
├── README.md
├── data/inventory.csv
├── sql/schema.sql
├── src/inventory_analysis.py
└── tests/test_inventory.py
```

## Run on Windows (VS Code)

Open this folder in VS Code, then select **Terminal → New Terminal**.

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
```

PowerShell activation may be blocked by Windows policy. You can skip activation and use the environment's Python executable directly in the commands below.

### 2. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Start the dashboard

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`.

### 4. Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Dataset columns

| Column | Meaning |
|---|---|
| `product_id` | Unique product code |
| `product_name` | Product name |
| `category` | Product category |
| `supplier` | Supplier name |
| `recorded_qty` | Quantity recorded in the inventory system |
| `physical_qty` | Quantity counted during physical audit |
| `reorder_level` | Trigger threshold for low stock |
| `max_stock_level` | Target upper stock threshold |
| `unit_cost` | Cost per unit in INR |
| `last_restocked` | Date of last restock |

## Business rules

- **Out of stock:** physical quantity is zero.
- **Low stock:** physical quantity is above zero and below reorder level.
- **Overstock:** physical quantity exceeds maximum stock level.
- **Normal:** none of the above.
- **Variance:** physical quantity minus recorded quantity. Negative variance means fewer units were counted than recorded.
- **Inventory value:** physical quantity × unit cost.
- **Suggested reorder quantity:** maximum stock level minus physical quantity, when physical quantity is below reorder level.

A production deployment should define whether stock status takes priority over audit discrepancies, track dated audit snapshots, and apply business-specific rules.

## MySQL setup (optional)

1. Open MySQL Workbench or your MySQL client.
2. Run `sql/schema.sql` to create the database and tables.
3. Load product and audit data into `products` and `stock_audit` using your preferred import workflow.

The Streamlit app currently reads the included CSV or an uploaded CSV; the SQL schema is provided for learning and extending the project to MySQL. It does not automatically connect to MySQL.

## GitHub

Before committing, review `.gitignore`, remove private data and secrets, then:

```bash
git init
git add .
git commit -m "Build inventory stock level audit dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```
