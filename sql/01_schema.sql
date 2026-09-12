-- ============================================================
-- TechBozor — Onlayn Elektronika Do'koni Ma'lumotlar Bazasi
-- Muallif: Mahammadjanova Gulnoza
-- Tavsif: Ushbu skript do'kon tizimining relatsion (PostgreSQL)
-- ma'lumotlar bazasi tuzilishini yaratadi.
-- ============================================================

-- Eski jadvallarni tozalash (qayta ishga tushirish uchun)
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- ------------------------------------------------------------
-- 1. CUSTOMERS — mijozlar
-- ------------------------------------------------------------
CREATE TABLE customers (
    customer_id     SERIAL PRIMARY KEY,
    full_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(150) UNIQUE NOT NULL,
    city            VARCHAR(50),
    registered_at   DATE NOT NULL DEFAULT CURRENT_DATE
);

-- ------------------------------------------------------------
-- 2. CATEGORIES — mahsulot toifalari
-- ------------------------------------------------------------
CREATE TABLE categories (
    category_id     SERIAL PRIMARY KEY,
    category_name   VARCHAR(50) UNIQUE NOT NULL
);

-- ------------------------------------------------------------
-- 3. PRODUCTS — mahsulotlar
--    FOREIGN KEY: category_id -> categories(category_id)
-- ------------------------------------------------------------
CREATE TABLE products (
    product_id      SERIAL PRIMARY KEY,
    sku             VARCHAR(30) UNIQUE NOT NULL,   -- mahsulot kodi (UPSERT uchun)
    product_name    VARCHAR(150) NOT NULL,
    category_id     INT REFERENCES categories(category_id) ON DELETE SET NULL,
    price           DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock           INT NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

-- ------------------------------------------------------------
-- 4. ORDERS — buyurtmalar (bosh jadval)
--    FOREIGN KEY: customer_id -> customers(customer_id)
-- ------------------------------------------------------------
CREATE TABLE orders (
    order_id        SERIAL PRIMARY KEY,
    customer_id     INT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    order_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending','completed','cancelled'))
);

-- ------------------------------------------------------------
-- 5. ORDER_ITEMS — junction table (Many-to-Many: orders <-> products)
--    Bitta buyurtmada bir nechta mahsulot, bitta mahsulot
--    bir nechta buyurtmada bo'lishi mumkin.
-- ------------------------------------------------------------
CREATE TABLE order_items (
    order_id        INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id      INT NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity        INT NOT NULL CHECK (quantity > 0),
    unit_price      DECIMAL(10,2) NOT NULL,   -- xarid vaqtidagi narx (tarixni saqlash uchun)
    PRIMARY KEY (order_id, product_id)         -- composite PRIMARY KEY
);

-- ------------------------------------------------------------
-- INDEXLAR — tez-tez qidiriladigan ustunlar uchun
-- (PRIMARY KEY va UNIQUE avtomatik index oladi, qolganlariga qo'lda qo'shamiz)
-- ------------------------------------------------------------
CREATE INDEX idx_orders_customer   ON orders (customer_id);
CREATE INDEX idx_orders_date       ON orders (order_date);
CREATE INDEX idx_products_category ON products (category_id);

-- ------------------------------------------------------------
-- Tuzilishni tekshirish
-- ------------------------------------------------------------
\dt
