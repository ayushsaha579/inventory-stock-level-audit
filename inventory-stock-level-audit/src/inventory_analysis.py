"""Core calculations for the Inventory Stock Level Audit project."""
from __future__ import annotations
import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "product_id", "product_name", "category", "supplier",
    "recorded_qty", "physical_qty", "reorder_level",
    "max_stock_level", "unit_cost", "last_restocked"
}

def validate_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """Validate columns and normalize types; returns a cleaned copy."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    out = df.copy()
    numeric_cols = ["recorded_qty", "physical_qty", "reorder_level", "max_stock_level", "unit_cost"]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    if out[numeric_cols].isna().any().any():
        raise ValueError("Numeric inventory fields contain blank or non-numeric values.")
    if (out[["recorded_qty", "physical_qty", "reorder_level", "max_stock_level"]] < 0).any().any():
        raise ValueError("Quantities and stock thresholds cannot be negative.")
    if (out["unit_cost"] < 0).any():
        raise ValueError("Unit cost cannot be negative.")
    if out["product_id"].duplicated().any():
        raise ValueError("product_id values must be unique.")
    out["last_restocked"] = pd.to_datetime(out["last_restocked"], errors="coerce")
    if out["last_restocked"].isna().any():
        raise ValueError("last_restocked contains invalid dates.")
    out["product_name"] = out["product_name"].astype(str).str.strip()
    out["category"] = out["category"].astype(str).str.strip()
    out["supplier"] = out["supplier"].astype(str).str.strip()
    return out

def audit_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """Add audit status, variance, valuation, and reorder recommendation."""
    out = validate_inventory(df)
    out["variance"] = out["physical_qty"] - out["recorded_qty"]
    out["variance_value"] = out["variance"] * out["unit_cost"]
    out["inventory_value"] = out["physical_qty"] * out["unit_cost"]
    out["stock_status"] = np.select(
        [
            out["physical_qty"].eq(0),
            out["physical_qty"].lt(out["reorder_level"]),
            out["physical_qty"].gt(out["max_stock_level"]),
        ],
        ["Out of stock", "Low stock", "Overstock"],
        default="Normal",
    )
    out["reorder_qty"] = np.where(
        out["physical_qty"] < out["reorder_level"],
        np.maximum(out["max_stock_level"] - out["physical_qty"], 0),
        0,
    ).astype(int)
    out["audit_status"] = np.where(out["variance"].eq(0), "Match", "Discrepancy")
    return out

def summary_metrics(audited: pd.DataFrame) -> dict:
    """Summarize an already audited inventory dataframe."""
    return {
        "total_products": int(audited["product_id"].nunique()),
        "total_units": int(audited["physical_qty"].sum()),
        "inventory_value": float(audited["inventory_value"].sum()),
        "low_stock": int(audited["stock_status"].eq("Low stock").sum()),
        "out_of_stock": int(audited["stock_status"].eq("Out of stock").sum()),
        "overstock": int(audited["stock_status"].eq("Overstock").sum()),
        "discrepancies": int(audited["audit_status"].eq("Discrepancy").sum()),
        "absolute_variance_value": float(audited["variance_value"].abs().sum()),
    }
