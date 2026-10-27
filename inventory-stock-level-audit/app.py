from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.inventory_analysis import audit_inventory, summary_metrics

st.set_page_config(page_title="Inventory Stock Level Audit", page_icon="📦", layout="wide")
st.title("📦 Inventory Stock Level Audit")
st.caption("Monitor stock, identify discrepancies, and prioritize replenishment.")

default_csv = ROOT / "data" / "inventory.csv"
uploaded = st.sidebar.file_uploader("Upload inventory CSV (optional)", type=["csv"])
try:
    raw = pd.read_csv(uploaded) if uploaded else pd.read_csv(default_csv)
    audited = audit_inventory(raw)
except Exception as exc:
    st.error(f"Could not load or audit inventory data: {exc}")
    st.info("Use the sample data/inventory.csv as a template. Required columns are documented in README.md.")
    st.stop()

st.sidebar.header("Filters")
categories = sorted(audited["category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
statuses = ["Out of stock", "Low stock", "Normal", "Overstock"]
selected_statuses = st.sidebar.multiselect("Stock status", statuses, default=statuses)
audit_options = ["Match", "Discrepancy"]
selected_audit = st.sidebar.multiselect("Audit result", audit_options, default=audit_options)

filtered = audited[
    audited["category"].isin(selected_categories)
    & audited["stock_status"].isin(selected_statuses)
    & audited["audit_status"].isin(selected_audit)
].copy()

m = summary_metrics(filtered)
def money(v):
    return f"₹{v:,.2f}"

k1, k2, k3, k4 = st.columns(4)
k1.metric("Products (filtered)", f"{m['total_products']:,}")
k2.metric("Physical units", f"{m['total_units']:,}")
k3.metric("Inventory value", money(m["inventory_value"]))
k4.metric("Audit discrepancies", f"{m['discrepancies']:,}")

k5, k6, k7, k8 = st.columns(4)
k5.metric("Low stock", f"{m['low_stock']:,}")
k6.metric("Out of stock", f"{m['out_of_stock']:,}")
k7.metric("Overstock", f"{m['overstock']:,}")
k8.metric("Absolute variance value", money(m["absolute_variance_value"]))

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Stock status distribution")
    status_counts = filtered["stock_status"].value_counts().reindex(statuses, fill_value=0)
    fig, ax = plt.subplots(figsize=(7, 4))
    status_counts.plot(kind="bar", ax=ax)
    ax.set_xlabel("Status")
    ax.set_ylabel("Products")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
with right:
    st.subheader("Inventory value by category")
    cat_value = filtered.groupby("category")["inventory_value"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    cat_value.plot(kind="bar", ax=ax)
    ax.set_xlabel("Category")
    ax.set_ylabel("Value (₹)")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.subheader("Products requiring attention")
attention = filtered[
    filtered["stock_status"].isin(["Out of stock", "Low stock", "Overstock"])
    | filtered["audit_status"].eq("Discrepancy")
].sort_values(["stock_status", "variance"], ascending=[True, True])
display_cols = [
    "product_id", "product_name", "category", "supplier", "recorded_qty",
    "physical_qty", "variance", "reorder_level", "max_stock_level",
    "stock_status", "audit_status", "reorder_qty", "unit_cost",
    "inventory_value", "variance_value"
]
st.dataframe(attention[display_cols], use_container_width=True, hide_index=True)

st.subheader("Full inventory audit")
search = st.text_input("Search product, category, or supplier")
full = filtered.copy()
if search:
    mask = (
        full["product_name"].str.contains(search, case=False, na=False)
        | full["category"].str.contains(search, case=False, na=False)
        | full["supplier"].str.contains(search, case=False, na=False)
        | full["product_id"].astype(str).str.contains(search, case=False, na=False)
    )
    full = full[mask]
st.dataframe(full[display_cols + ["last_restocked"]], use_container_width=True, hide_index=True)

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered audit CSV", data=csv_bytes, file_name="inventory_audit_report.csv", mime="text/csv")

st.caption("Demo dataset for learning purposes. Physical counts and stock thresholds should be verified against real business records.")
