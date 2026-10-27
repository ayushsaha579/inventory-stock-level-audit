-- Inventory Stock Level Audit schema (MySQL 8+)
CREATE DATABASE IF NOT EXISTS inventory_audit;
USE inventory_audit;

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(80) NOT NULL,
    supplier VARCHAR(120) NOT NULL,
    reorder_level INT NOT NULL DEFAULT 0,
    max_stock_level INT NOT NULL DEFAULT 0,
    unit_cost DECIMAL(12,2) NOT NULL DEFAULT 0,
    last_restocked DATE,
    CHECK (reorder_level >= 0),
    CHECK (max_stock_level >= reorder_level),
    CHECK (unit_cost >= 0)
);

CREATE TABLE IF NOT EXISTS stock_audit (
    audit_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL,
    recorded_qty INT NOT NULL,
    physical_qty INT NOT NULL,
    audit_date DATE NOT NULL,
    notes VARCHAR(500),
    CONSTRAINT fk_stock_audit_product FOREIGN KEY (product_id) REFERENCES products(product_id),
    CHECK (recorded_qty >= 0),
    CHECK (physical_qty >= 0)
);

-- Example audit report query
SELECT p.product_id, p.product_name, p.category, p.supplier,
       a.recorded_qty, a.physical_qty,
       a.physical_qty - a.recorded_qty AS variance,
       (a.physical_qty - a.recorded_qty) * p.unit_cost AS variance_value,
       a.physical_qty * p.unit_cost AS inventory_value,
       CASE
         WHEN a.physical_qty = 0 THEN 'Out of stock'
         WHEN a.physical_qty < p.reorder_level THEN 'Low stock'
         WHEN a.physical_qty > p.max_stock_level THEN 'Overstock'
         ELSE 'Normal'
       END AS stock_status
FROM products p
JOIN stock_audit a ON a.product_id = p.product_id
WHERE a.audit_date = (SELECT MAX(a2.audit_date) FROM stock_audit a2 WHERE a2.product_id = p.product_id);

-- Products requiring replenishment
SELECT product_id, product_name, physical_qty, reorder_level,
       GREATEST(max_stock_level - physical_qty, 0) AS suggested_reorder_qty
FROM (
    SELECT p.product_id, p.product_name, p.reorder_level, p.max_stock_level,
           a.physical_qty
    FROM products p
    JOIN stock_audit a ON a.product_id = p.product_id
) AS current_stock
WHERE physical_qty < reorder_level;

-- Inventory value by category (using latest audit row per product in a production system)
SELECT p.category, SUM(a.physical_qty * p.unit_cost) AS inventory_value
FROM products p
JOIN stock_audit a ON a.product_id = p.product_id
GROUP BY p.category
ORDER BY inventory_value DESC;
