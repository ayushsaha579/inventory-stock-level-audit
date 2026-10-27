import pandas as pd
from src.inventory_analysis import audit_inventory, summary_metrics

def sample():
    return pd.DataFrame([
        {"product_id":"P1","product_name":"Mouse","category":"Accessories","supplier":"S1","recorded_qty":10,"physical_qty":5,"reorder_level":8,"max_stock_level":30,"unit_cost":100,"last_restocked":"2026-01-01"},
        {"product_id":"P2","product_name":"Cable","category":"Accessories","supplier":"S2","recorded_qty":0,"physical_qty":0,"reorder_level":5,"max_stock_level":20,"unit_cost":50,"last_restocked":"2026-01-02"},
        {"product_id":"P3","product_name":"Monitor","category":"Displays","supplier":"S3","recorded_qty":20,"physical_qty":25,"reorder_level":5,"max_stock_level":20,"unit_cost":5000,"last_restocked":"2026-01-03"},
    ])

def test_status_and_variance():
    out = audit_inventory(sample()).set_index("product_id")
    assert out.loc["P1", "stock_status"] == "Low stock"
    assert out.loc["P2", "stock_status"] == "Out of stock"
    assert out.loc["P3", "stock_status"] == "Overstock"
    assert out.loc["P1", "variance"] == -5

def test_summary_metrics():
    out = audit_inventory(sample())
    metrics = summary_metrics(out)
    assert metrics["total_products"] == 3
    assert metrics["low_stock"] == 1
    assert metrics["out_of_stock"] == 1
    assert metrics["overstock"] == 1
