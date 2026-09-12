-- ============================================================
-- TechBozor — Analitik SQL so'rovlar (JUNIOR versiya)
-- Faqat asosiy SQL: SELECT, WHERE, JOIN, GROUP BY, ORDER BY, LIMIT
-- (CTE, Window Function va UPSERT olib tashlandi — bular Junior
--  daraja uchun ortiqcha murakkab, keyinroq o'rganiladi)
-- ============================================================


-- ------------------------------------------------------------
-- 1. Har bir kategoriya bo'yicha jami sotuv va buyurtmalar soni
-- ------------------------------------------------------------
SELECT
    c.category_name,
    COUNT(DISTINCT o.order_id)                 AS total_orders,
    SUM(oi.quantity * oi.unit_price)           AS total_revenue,
    ROUND(AVG(oi.quantity * oi.unit_price), 2) AS avg_item_value
FROM categories c
JOIN products p    ON p.category_id = c.category_id
JOIN order_items oi ON oi.product_id = p.product_id
JOIN orders o       ON o.order_id = oi.order_id
WHERE o.status = 'completed'
GROUP BY c.category_name
ORDER BY total_revenue DESC;


-- ------------------------------------------------------------
-- 2. Har oy bo'yicha jami sotuv (trend uchun)
-- ------------------------------------------------------------
SELECT
    DATE_TRUNC('month', o.order_date)::DATE AS month,
    SUM(oi.quantity * oi.unit_price)        AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;


-- ------------------------------------------------------------
-- 3. Har bir mijozning nechta buyurtma bergani va jami xarajati
--    (RFM o'rniga oddiy JOIN + GROUP BY)
-- ------------------------------------------------------------
SELECT
    cu.customer_id,
    cu.full_name,
    cu.city,
    COUNT(DISTINCT o.order_id)       AS order_count,
    SUM(oi.quantity * oi.unit_price) AS total_spent
FROM customers cu
JOIN orders o       ON o.customer_id = cu.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY cu.customer_id, cu.full_name, cu.city
ORDER BY total_spent DESC
LIMIT 15;


-- ------------------------------------------------------------
-- 4. Eng ko'p sotilgan Top-5 mahsulot
--    (RANK() Window Function o'rniga oddiy ORDER BY + LIMIT)
-- ------------------------------------------------------------
SELECT
    p.product_name,
    SUM(oi.quantity)                 AS units_sold,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
JOIN orders o        ON o.order_id = oi.order_id
WHERE o.status = 'completed'
GROUP BY p.product_name
ORDER BY units_sold DESC
LIMIT 5;


-- ------------------------------------------------------------
-- 5. "Bir martalik" va "qayta xarid qilgan" mijozlarni ajratish
--    (GROUP BY natijasini HAVING bilan filtrlash)
-- ------------------------------------------------------------
SELECT
    cu.customer_id,
    cu.full_name,
    COUNT(DISTINCT o.order_id) AS order_count
FROM customers cu
JOIN orders o ON o.customer_id = cu.customer_id
WHERE o.status = 'completed'
GROUP BY cu.customer_id, cu.full_name
HAVING COUNT(DISTINCT o.order_id) >= 5
ORDER BY order_count DESC;


-- ------------------------------------------------------------
-- 6. Mahsulot narxini yangilash (oddiy UPDATE)
--    (ON CONFLICT/UPSERT o'rniga oddiy UPDATE ... WHERE)
-- ------------------------------------------------------------
UPDATE products
SET price = 749.00,
    stock = 40
WHERE sku = 'SKU-1001';
